import pandas as pd
import numpy as np
import re


def _parse_height(value: str) -> float | None:
    if pd.isna(value):
        return None
    text = str(value).lower()
    if 'cm' in text:
        parts = [p for p in text.split() if p.endswith('cm')]
        for part in parts:
            try:
                return float(part.replace('cm', '').strip())
            except ValueError:
                continue
    if 'ft' in text or 'in' in text:
        nums = [float(n) for n in re.findall(r'\d+\.?\d*', text)]
        if len(nums) >= 2:
            feet, inches = nums[0], nums[1]
            return round(feet * 30.48 + inches * 2.54, 1)
    return None


def _parse_weight(value: str) -> float | None:
    if pd.isna(value):
        return None
    text = str(value).lower()
    if 'kg' in text:
        parts = [p for p in text.split() if p.endswith('kg')]
        for part in parts:
            try:
                return float(part.replace('kg', '').strip())
            except ValueError:
                continue
    if 'lb' in text or 'lbs' in text:
        nums = [float(n) for n in re.findall(r'\d+\.?\d*', text)]
        if nums:
            return round(nums[0] * 0.45359237, 1)
    return None


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    out = df.copy()
    out['height_cm'] = out.get('height_cm')
    if 'height_cm' not in out.columns or out['height_cm'].isna().all():
        if 'height' in out.columns:
            out['height_cm'] = out['height'].apply(_parse_height)

    out['weight_kg'] = out.get('weight_kg')
    if 'weight_kg' not in out.columns or out['weight_kg'].isna().all():
        if 'weight' in out.columns:
            out['weight_kg'] = out['weight'].apply(_parse_weight)

    if 'birth_date' in out.columns:
        out['birth_date'] = pd.to_datetime(out['birth_date'], errors='coerce')
        out['edad'] = out['birth_date'].apply(lambda dt: np.nan if pd.isna(dt) else (pd.Timestamp.now().year - dt.year))
    else:
        out['edad'] = np.nan

    if 'debut' in out.columns:
        out['debut'] = out['debut'].astype(str).str.extract(r'(\d{4})')[0]
        out['experiencia_anos'] = pd.to_numeric(out['debut'], errors='coerce').apply(
            lambda y: np.nan if pd.isna(y) else max(0, pd.Timestamp.now().year - int(y))
        )
    else:
        out['experiencia_anos'] = np.nan

    out['promedio_combates_por_año'] = np.nan
    if 'total_matches' in out.columns and 'experiencia_anos' in out.columns:
        out['promedio_combates_por_año'] = out.apply(
            lambda row: row['total_matches'] / row['experiencia_anos']
            if pd.notna(row['total_matches']) and pd.notna(row['experiencia_anos']) and row['experiencia_anos'] > 0
            else np.nan,
            axis=1,
        )

    if 'era' in out.columns:
        out['era'] = out['era'].fillna('Sin clasificar')

    for col in ['num_titles', 'total_titles', 'total_reigns', 'total_wins', 'total_losses', 'total_matches']:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors='coerce').fillna(0)

    if 'total_wins' in out.columns and 'total_matches' in out.columns:
        out['ratio_victorias'] = out.apply(
            lambda row: row['total_wins'] / row['total_matches'] if row['total_matches'] > 0 else 0,
            axis=1,
        )
    else:
        out['ratio_victorias'] = np.nan

    if 'total_titles' in out.columns:
        out['total_titulos'] = out['total_titles']
    else:
        out['total_titulos'] = 0

    if 'total_reign' in out.columns:
        out['total_reinados'] = out['total_reign']
    elif 'champion_reign_number' in out.columns:
        out['total_reinados'] = pd.to_numeric(out['champion_reign_number'], errors='coerce').fillna(0)
    else:
        out['total_reinados'] = 0

    return out
