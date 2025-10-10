import os
import json
import typing as t

import gradio as gr
import requests

DEFAULT_BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")
DEFAULT_API_KEY = os.getenv("API_KEY", "")

def parse_schema_attributes(raw: str) -> t.List[str]:
    if not raw.strip():
        return []
    return [s.strip() for s in raw.split(",") if s.strip()]

def tidy_values(values: t.List[str]) -> t.List[str]:
    unique: t.Dict[str, str] = {}
    for v in values:
        if not isinstance(v, str):
            continue
        v_stripped = v.strip()
        if not v_stripped or v_stripped.lower() == "n/a":
            continue
        key = v_stripped.lower()
        if key not in unique:
            unique[key] = v_stripped
    return list(unique.values())


def merge_attributes(non_targeted: dict, targeted: dict) -> dict:
    # Merge by attribute name; prioritize targeted presence; dedupe values; drop N/A
    merged: t.Dict[str, t.Set[str]] = {}
    order: t.List[str] = []

    def add_attrs(src: dict, prefer: bool) -> None:
        for item in src.get("attributes", []):
            name = item.get("name")
            vals = item.get("value", [])
            if not isinstance(vals, list):
                vals = [str(vals)]
            vals = tidy_values(vals)
            if not name or not isinstance(name, str):
                continue
            if name not in merged:
                merged[name] = set()
                order.append(name)
            # If prefer (targeted), union as usual; for non-targeted also union
            merged[name].update(vals)

    # Prefer targeted by adding it last to ensure presence, but we don't remove non-targeted values
    add_attrs(non_targeted or {}, prefer=False)
    add_attrs(targeted or {}, prefer=True)

    return {
        "attributes": [
            {"name": name, "value": sorted(list(values))}
            for name, values in ((n, merged[n]) for n in order)
            if values
        ]
    }


def call_api(mode: str, title: str, description: str, schema_attributes_csv: str, base_url: str, api_key: str) -> t.Tuple[str, str, str]:
    base_url = base_url.strip() or DEFAULT_BASE_URL
    api_key = api_key.strip() or DEFAULT_API_KEY
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["x-api-key"] = api_key

    schema_attributes = parse_schema_attributes(schema_attributes_csv)

    exploratory_json = {}
    targeted_json = {}
    merged_json = {}

    session = requests.Session()

    if mode in ("Exploratory", "Combined"):
        resp = session.post(
            f"{base_url}/extract",
            headers=headers,
            data=json.dumps({"title": title, "description": description}),
            timeout=60,
        )
        resp.raise_for_status()
        exploratory_json = resp.json()

    if mode in ("Targeted", "Combined"):
        resp = session.post(
            f"{base_url}/extract-targeted",
            headers=headers,
            data=json.dumps({
                "title": title,
                "description": description,
                "schema_attributes": schema_attributes,
            }),
            timeout=60,
        )
        resp.raise_for_status()
        targeted_json = resp.json()

    if mode == "Combined":
        merged_json = merge_attributes(exploratory_json, targeted_json)

    # Return pretty JSON strings for display
    def pretty(d: dict) -> str:
        return json.dumps(d, indent=2, ensure_ascii=False) if d else ""

    return pretty(exploratory_json), pretty(targeted_json), pretty(merged_json)


def build_ui() -> gr.Blocks:
    with gr.Blocks(title="Attribute Extraction Demo") as demo:
        gr.Markdown("""
        ### Attribute Extraction Demo
        - Enter a title and description.
        - Choose mode: Exploratory, Targeted, or Combined (client-side merge).
        - For Targeted/Combined, provide comma-separated schema attributes (e.g., Color, Size, Material).
        """)

        with gr.Row():
            title = gr.Textbox(label="Title", placeholder="Product title")
            base_url = gr.Textbox(label="Base URL", value=DEFAULT_BASE_URL)
        description = gr.Textbox(label="Description", lines=5, placeholder="Product description")
        schema_csv = gr.Textbox(label="Schema Attributes (comma-separated)")
        with gr.Row():
            mode = gr.Radio(["Exploratory", "Targeted", "Combined"], value="Exploratory", label="Mode")
            api_key = gr.Textbox(label="API Key (x-api-key)", type="password", value=DEFAULT_API_KEY)
        run_btn = gr.Button("Run")

        gr.Markdown("### Results")
        with gr.Row():
            out_exp = gr.Code(label="Exploratory JSON", language="json")
            out_tgt = gr.Code(label="Targeted JSON", language="json")
        out_merge = gr.Code(label="Combined (client-side) JSON", language="json")

        run_btn.click(
            fn=call_api,
            inputs=[mode, title, description, schema_csv, base_url, api_key],
            outputs=[out_exp, out_tgt, out_merge],
        )

    return demo


if __name__ == "__main__":
    ui = build_ui()
    ui.launch(server_name="0.0.0.0", server_port=7860, share=False)
