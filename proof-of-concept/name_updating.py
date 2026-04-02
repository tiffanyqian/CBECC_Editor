import pandas as pd
import re
from pathlib import Path

def replace_strings_in_xml_from_csv(
    xml_input_path: Path,
    xml_output_path: Path,
    csv_mapping_path: Path,
    from_col: str = "from_text",
    to_col: str = "to_text",
    encoding: str = "utf-8"
):
    """
    Replace all substring occurrences in an XML file using a CSV mapping file.
    The XML is treated as raw text to preserve structure and formatting.
    """

    # --- Load mapping CSV ---
    mapping_df = pd.read_csv(csv_mapping_path)

    # Validate columns
    if from_col not in mapping_df.columns or to_col not in mapping_df.columns:
        raise ValueError(
            f"CSV must contain columns '{from_col}' and '{to_col}'"
        )

    # Drop invalid rows
    mapping_df = mapping_df.dropna(subset=[from_col, to_col])

    # Build replacement dictionary
    replacements = dict(zip(mapping_df[from_col], mapping_df[to_col]))

    if not replacements:
        raise ValueError("No valid replacement pairs found in CSV.")

    # --- Read XML as raw text ---
    xml_text = xml_input_path.read_text(encoding=encoding)

    # --- Build regex pattern (longest-first prevents partial overlaps) ---
    keys_sorted = sorted(replacements.keys(), key=len, reverse=True)
    pattern = re.compile("|".join(re.escape(k) for k in keys_sorted))

    # --- Replacement function ---
    def replacer(match):
        return replacements[match.group(0)]

    # --- Apply replacements ---
    updated_xml = pattern.sub(replacer, xml_text)

    # --- Write output XML ---
    xml_output_path.write_text(updated_xml, encoding=encoding)


if __name__ == "__main__":
    replace_strings_in_xml_from_csv(
        xml_input_path=Path(r"C:\Models\26.19 SHC\IES\2950 Tech Offc\2950 SHC - SD T24\2950 SHC - SD T24.xml"),
        xml_output_path=Path(r"C:\Models\26.19 SHC\IES\2950 Tech Offc\2950 SHC - SD T24\Case 0 - 2950 Envelope Only.cibd22x"),
        csv_mapping_path=Path(r"C:\Models\26.19 SHC\IES\2950 Tech Offc\2950 SHC - SD T24\mapping.csv"),
        from_col="from_text",
        to_col="to_text"
    )

    print("✅ XML replacement complete.")