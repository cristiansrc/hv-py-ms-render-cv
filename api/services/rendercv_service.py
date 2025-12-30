from __future__ import annotations

import base64
import pathlib
import tempfile
from collections.abc import Mapping
from typing import Any, get_args

from ruamel.yaml import YAML

from rendercv.exception import RenderCVInternalError
from rendercv.renderer.pdf_png import generate_pdf
from rendercv.renderer.typst import generate_typst
from rendercv.schema.models.cv.section import get_entry_type_name_and_section_model
from rendercv.schema.models.design.design import validate_design
from rendercv.schema.models.locale.locale import Locale, locale_adapter
from rendercv.schema.rendercv_model_builder import build_rendercv_dictionary_and_model


def _dump_payload_to_yaml(payload: dict[str, Any], yaml_path: pathlib.Path) -> None:
    yaml = YAML()
    yaml.default_flow_style = False
    with yaml_path.open("w", encoding="utf-8") as handle:
        yaml.dump(payload, handle)


def render_pdf_base64(payload: dict[str, Any]) -> str:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = pathlib.Path(tmpdir)
        yaml_path = tmp_path / "cv.yaml"
        _dump_payload_to_yaml(payload, yaml_path)

        _, model = build_rendercv_dictionary_and_model(
            yaml_path,
            typst_path=tmp_path / "cv.typ",
            pdf_path=tmp_path / "cv.pdf",
            dont_generate_html=True,
            dont_generate_markdown=True,
            dont_generate_png=True,
        )

        _apply_inline_overrides(payload, model)

        typst_path = generate_typst(model)
        pdf_path = generate_pdf(model, typst_path)

        if pdf_path is None or not pdf_path.exists():
            raise RenderCVInternalError("PDF generation failed.")

        pdf_bytes = pdf_path.read_bytes()

    return base64.b64encode(pdf_bytes).decode("ascii")


def _normalize_section_entries(model: Any) -> None:
    sections = getattr(model.cv, "sections", None)
    if not sections:
        return

    for title, entries in sections.items():
        if not entries:
            continue
        if all(
            isinstance(entry, str) or hasattr(entry, "entry_type_in_snake_case")
            for entry in entries
        ):
            continue
        entry_type_name, section_type = get_entry_type_name_and_section_model(entries[0])
        section = {
            "title": "Normalized Section",
            "entry_type": entry_type_name,
            "entries": entries,
        }
        section_object = section_type.model_validate(section)
        sections[title] = section_object.entries


def _apply_inline_overrides(payload: dict[str, Any], model: Any) -> None:
    _normalize_section_entries(model)

    model.locale = _coerce_locale(payload.get("locale", model.locale))

    model.design = _coerce_design(payload.get("design", model.design))


def _coerce_locale(locale_payload: Any) -> Any:
    if locale_payload is None or hasattr(locale_payload, "month_names"):
        return locale_payload

    if isinstance(locale_payload, Mapping):
        language = locale_payload.get("language")
        locale_classes = get_args(get_args(Locale)[0])
        for locale_cls in locale_classes:
            default_language = locale_cls.model_fields["language"].default
            if default_language == language:
                return locale_cls.model_validate(locale_payload)

    return locale_adapter.validate_python(locale_payload)


def _coerce_design(design_payload: Any) -> Any:
    if design_payload is None or hasattr(design_payload, "theme"):
        return design_payload

    if isinstance(design_payload, Mapping):
        return validate_design(design_payload, None)

    return design_payload
