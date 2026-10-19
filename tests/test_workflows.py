from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


audit = load("audit", "skills/zotero-docx-reference-workflow/scripts/inspect_zotero_docx.py")
connector = load("connector", "skills/zotero-docx-reference-workflow/scripts/zotero_connector.py")
figures = load("figures", "skills/publication-chart-skill/scripts/make_framework.py")
installer = load("installer", "tools/install_skills.py")
W = audit.W


def para(parent, text=None):
    p = ET.SubElement(parent, W + "p")
    if text is not None:
        ET.SubElement(ET.SubElement(p, W + "r"), W + "t").text = text
    return p


def mark(parent, kind):
    ET.SubElement(ET.SubElement(parent, W + "r"), W + "fldChar", {W + "fldCharType": kind})


def instruction(parent, text):
    ET.SubElement(ET.SubElement(parent, W + "r"), W + "instrText").text = text


def shown(parent, text):
    ET.SubElement(ET.SubElement(parent, W + "r"), W + "t").text = text


def citation(parent, keys, display="[1]", cid="citation-01", local_id=731):
    data = {"citationID": cid, "properties": {"plainCitation": display, "formattedCitation": display},
            "citationItems": [{"id": local_id + index, "uris": [f"http://zotero.org/users/local/EXAMPLE/items/{key}"],
                               "itemData": {"title": "Synthetic example"}}
                              for index, key in enumerate(keys)]}
    mark(parent, "begin")
    # Real Word may split a single instruction over multiple runs.
    payload = " ADDIN ZOTERO_ITEM CSL_CITATION " + json.dumps(data)
    instruction(parent, payload[:55])
    instruction(parent, payload[55:])
    mark(parent, "separate")
    shown(parent, display)
    mark(parent, "end")


class DocxAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = ET.Element(W + "document")
        self.body = ET.SubElement(self.root, W + "body")

    def inspect(self, extra_parts=None):
        path = Path(self.tmp.name) / "synthetic.docx"
        with ZipFile(path, "w") as package:
            package.writestr("word/document.xml", ET.tostring(self.root))
            for name, content in (extra_parts or {}).items():
                package.writestr(name, content)
        return audit.inspect_docx(path)

    def test_multiple_fields_same_paragraph_and_uri_identity(self):
        p = para(self.body)
        citation(p, ["SYNTH001"])
        citation(p, ["SYNTH002"], "[2]", "citation-02", local_id=731)
        citation(p, ["SYNTH001"], "[1]", "citation-03", local_id=987)
        result = self.inspect()
        self.assertEqual(result["zotero_item_fields"], 3)
        self.assertEqual(result["unique_cited_items"], 2)
        self.assertEqual(result["numbered_sequence_mismatches"], [])

    def test_bibliography_spans_paragraphs(self):
        citation(para(self.body), ["SYNTH001"])
        para(self.body, "References")
        first = para(self.body)
        mark(first, "begin")
        instruction(first, ' ADDIN ZOTERO_BIBL {"uncited":[]} CSL_BIBLIOGRAPHY ')
        mark(first, "separate")
        shown(first, "[1] Synthetic reference one")
        second = para(self.body, "[2] Synthetic reference two")
        mark(second, "end")
        result = self.inspect()
        self.assertEqual(result["zotero_bibl_fields"], 1)
        self.assertEqual(result["visible_numbered_references"], 2)
        self.assertIn("reference two", result["bibliography_fields"][0]["display"])
        self.assertEqual(result["unclosed_zotero_fields"], 0)

    def test_hidden_multi_item_field(self):
        citation(para(self.body), ["SYNTH001", "SYNTH002"], "[1]")
        result = self.inspect()
        self.assertEqual(result["multi_item_fields"], 1)
        self.assertEqual(result["unique_cited_items"], 2)

    def test_hyperlink_wrapper_and_deleted_fields(self):
        p = para(self.body)
        citation(ET.SubElement(p, W + "hyperlink"), ["SYNTH001"])
        citation(ET.SubElement(p, W + "del"), ["SYNTH002"], cid="deleted")
        self.assertEqual(self.inspect()["zotero_item_fields"], 1)

    def test_numbering_mismatch_does_not_change_identity(self):
        citation(para(self.body), ["SYNTH001"], "[9]")
        result = self.inspect()
        self.assertEqual(result["numbered_sequence_mismatches"][0]["expected"], "[1]")
        self.assertEqual(result["unique_cited_items"], 1)

    def test_empty_display_duplicate_id_and_bad_json(self):
        p = para(self.body)
        citation(p, ["SYNTH001"], "")
        citation(p, ["SYNTH002"], "[2]")
        mark(p, "begin")
        instruction(p, " ADDIN ZOTERO_ITEM CSL_CITATION {oops ")
        mark(p, "separate")
        shown(p, "[3]")
        mark(p, "end")
        result = self.inspect()
        self.assertEqual(result["empty_display_fields"], 1)
        self.assertEqual(result["json_parse_failures"], 1)
        self.assertEqual(result["duplicate_citation_ids"], ["citation-01"])

    def test_unclosed_field_and_preferences(self):
        p = para(self.body)
        mark(p, "begin")
        instruction(p, "ADDIN ZOTERO_BIBL")
        mark(p, "separate")
        props = b'<Properties><property name="ZOTERO_PREF_1"><value>example</value></property></Properties>'
        result = self.inspect({"docProps/custom.xml": props})
        self.assertEqual(result["unclosed_zotero_fields"], 1)
        self.assertTrue(result["document_preferences_present"])
        self.assertFalse(result["live_refresh_verified"])

    def test_footnotes_are_separate_story(self):
        citation(para(self.body), ["SYNTH001"])
        notes = ET.Element(W + "footnotes")
        citation(para(notes), ["SYNTH002"], "[8]", "note-citation")
        result = self.inspect({"word/footnotes.xml": ET.tostring(notes)})
        self.assertEqual(result["zotero_item_fields"], 2)
        self.assertEqual(result["numbered_sequence_mismatches"], [])


class FigureTests(unittest.TestCase):
    def setUp(self):
        self.font = figures.find_font(None)
        self.spec = json.loads((ROOT / "skills/publication-chart-skill/examples/framework.json").read_text(encoding="utf-8"))

    def test_editable_svg_peer_sizes_and_fit(self):
        svg, report = figures.render(self.spec, self.font)
        root = ET.fromstring(svg)
        self.assertGreater(len(list(root.iter(f"{{{figures.SVG}}}text"))), 5)
        self.assertTrue(report["fit_verified"])
        boxes = report["boxes"]
        self.assertEqual(boxes["problem"]["width"], boxes["evidence"]["width"])
        self.assertEqual(boxes["problem"]["width"], boxes["concept"]["width"])
        self.assertTrue(all(0 < value <= 0.90 for value in report["text_occupancy"].values()))

    def test_duplicate_nodes_and_wrong_edge_rejected(self):
        self.spec["rows"][0][1]["id"] = "problem"
        with self.assertRaisesRegex(ValueError, "Duplicate node"):
            figures.render(self.spec, self.font)
        self.spec["rows"][0][1]["id"] = "evidence"
        self.spec["edges"] = [["problem", "output"]]
        with self.assertRaisesRegex(ValueError, "adjacent"):
            figures.render(self.spec, self.font)

    def test_overflow_rejected(self):
        self.spec["rows"][0][0]["body"] = "word " * 2000
        with self.assertRaisesRegex(ValueError, "does not fit"):
            figures.render(self.spec, self.font)


class InstallationTests(unittest.TestCase):
    def test_skip_replace_backup_and_dry_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source" / "sample-skill"
            source.mkdir(parents=True)
            (source / "SKILL.md").write_text("original", encoding="utf-8")
            dest = root / "dest"
            self.assertEqual(installer.install(source, dest, dry_run=True)["action"], "would-install")
            self.assertFalse(dest.exists())
            installer.install(source, dest)
            (source / "SKILL.md").write_text("updated", encoding="utf-8")
            self.assertEqual(installer.install(source, dest)["action"], "skipped-existing")
            result = installer.install(source, dest, replace=True)
            self.assertEqual((Path(result["backup"]) / "SKILL.md").read_text(), "original")
            self.assertEqual((dest / source.name / "SKILL.md").read_text(), "updated")

    def test_overlap_rejected(self):
        source = ROOT / "skills/publication-chart-skill"
        with self.assertRaisesRegex(ValueError, "overlap"):
            installer.install(source, source)


class ConnectorTests(unittest.TestCase):
    def test_only_local_base_allowed(self):
        self.assertEqual(connector.validate_base("http://127.0.0.1:23119/"), "http://127.0.0.1:23119")
        for url in ("https://example.org", "http://127.0.0.1@evil.example", "http://localhost/?token=example"):
            with self.assertRaises(ValueError):
                connector.validate_base(url)

    def test_input_requires_real_item_shape(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "items.json"
            path.write_text(json.dumps({"items": [{"itemType": "book", "title": "Synthetic example"}]}))
            self.assertEqual(len(connector.load_items(path)), 1)
            path.write_text("[]")
            with self.assertRaises(ValueError):
                connector.load_items(path)


if __name__ == "__main__":
    unittest.main()
