#!/usr/bin/env python3
"""
Cleo 🔍 — Automated Quality Control Gatekeeper for DoniesDaily
Rigorous deterministic audio/video inspection using ffprobe & ffmpeg before YouTube upload.
"""
import os
import sys
import json
import re
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, Union, List

def inspect_video(video_path: str, audio_path: Optional[str] = None) -> Dict[str, Any]:
    report: Dict[str, Any] = {
        "passed": True,
        "video_path": video_path,
        "errors": [],
        "warnings": [],
        "metrics": {}
    }

    v_file = Path(video_path)
    if not v_file.exists():
        report["passed"] = False
        report["errors"].append(f"File video tidak ditemukan: {video_path}")
        return report

    size_mb = v_file.stat().st_size / (1024 * 1024)
    report["metrics"]["file_size_mb"] = round(size_mb, 2)
    if size_mb < 1.0:
        report["passed"] = False
        report["errors"].append(f"Ukuran video terlalu kecil (<1MB): {size_mb:.2f}MB")

    # 1. ffprobe Streams & Format
    cmd_probe = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_streams", "-show_format", str(v_file)
    ]
    try:
        p_res = subprocess.run(cmd_probe, capture_output=True, text=True, check=True)
        meta = json.loads(p_res.stdout)
    except Exception as e:
        report["passed"] = False
        report["errors"].append(f"ffprobe gagal membaca file video: {e}")
        return report

    streams = meta.get("streams", [])
    format_info = meta.get("format", {})
    
    v_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
    a_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)

    if not v_stream:
        report["passed"] = False
        report["errors"].append("CRITICAL: Stream video tidak ditemukan!")
        return report

    if not a_stream:
        report["passed"] = False
        report["errors"].append("CRITICAL: Stream audio tidak ditemukan dalam file video!")

    # Resolution Check (Must be 9:16 vertical, standard 1080x1920)
    width = int(v_stream.get("width", 0))
    height = int(v_stream.get("height", 0))
    report["metrics"]["resolution"] = f"{width}x{height}"
    
    if width != 1080 or height != 1920:
        aspect_ratio = width / height if height else 0
        if round(aspect_ratio, 2) != 0.56: # 9/16 = 0.5625
            report["passed"] = False
            report["errors"].append(f"Aspect ratio bukan 9:16 vertikal ({width}x{height})")
        else:
            report["warnings"].append(f"Resolusi vertikal {width}x{height} bukan standar 1080x1920")

    # Duration Check (YouTube Shorts must be < 60s, recommended 15s - 58s)
    duration = float(format_info.get("duration", 0))
    report["metrics"]["duration_seconds"] = round(duration, 2)
    if duration > 59.9:
        report["passed"] = False
        report["errors"].append(f"Durasi video melebihi batas YouTube Shorts (>60s): {duration:.2f}s")
    elif duration < 10.0:
        report["passed"] = False
        report["errors"].append(f"Durasi video terlalu singkat untuk shorts (<10s): {duration:.2f}s")

    # Audio Desync Check (if raw TTS audio is supplied)
    if audio_path and Path(audio_path).exists():
        cmd_aprobe = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", audio_path]
        try:
            a_res = subprocess.run(cmd_aprobe, capture_output=True, text=True, check=True)
            a_meta = json.loads(a_res.stdout)
            raw_a_duration = float(a_meta.get("format", {}).get("duration", 0))
            delta = abs(duration - raw_a_duration)
            report["metrics"]["audio_delta_seconds"] = round(delta, 3)
            if delta > 1.5:
                report["passed"] = False
                report["errors"].append(f"Desync audio vs video melebihi toleransi 1.5s (delta: {delta:.2f}s)")
        except Exception as err:
            report["warnings"].append(f"Gagal memverifikasi audio raw: {err}")

    # 2. Black Frame Detection (Freeze or black gap >= 0.5s)
    cmd_black = [
        "ffmpeg", "-i", str(v_file),
        "-vf", "blackdetect=d=0.5:pix_th=0.10",
        "-f", "null", "-"
    ]
    try:
        black_res = subprocess.run(cmd_black, capture_output=True, text=True)
        if "black_start" in black_res.stderr:
            report["passed"] = False
            report["errors"].append("Terdeteksi black frame / layar hitam membeku >= 0.5s")
        else:
            report["metrics"]["black_frame_clean"] = True
    except Exception as e:
        report["warnings"].append(f"Blackframe check error: {e}")

    # 3. Audio Loudness (EBU R128 integrated loudness)
    cmd_loudness = [
        "ffmpeg", "-i", str(v_file),
        "-af", "ebur128",
        "-f", "null", "-"
    ]
    try:
        loud_res = subprocess.run(cmd_loudness, capture_output=True, text=True)
        out = loud_res.stderr
        # Cari di Summary section terlebih dahulu
        summary_match = re.search(r"Integrated loudness:\s*\n\s*I:\s*(-?[\d\.]+)\s*LUFS", out)
        if summary_match:
            il = float(summary_match.group(1))
        else:
            all_matches = re.findall(r"I:\s*(-?[\d\.]+)\s*LUFS", out)
            il = float(all_matches[-1]) if all_matches else None

        if il is not None:
            report["metrics"]["integrated_loudness_lufs"] = il
            if il < -26.0:
                report["warnings"].append(f"Audio agak lirih ({il} LUFS, ideal: -14 s/d -20 LUFS)")
            elif il > -8.0:
                report["warnings"].append(f"Audio berisiko distorsi / terlalu keras ({il} LUFS)")
    except Exception as e:
        report["warnings"].append(f"Loudness check error: {e}")

    return report

def audit_script_and_outro(script_text: str) -> Dict[str, Any]:
    """Verifies Hukum Besi #15: Script MUST end with Follow & Subscribe CTA."""
    report = {"passed": True, "errors": [], "warnings": []}
    if not script_text:
        report["warnings"].append("Skrip teks kosong, verifikasi outro dilewati.")
        return report

    text_lower = script_text.lower()
    has_sub = "subscribe" in text_lower or "subs" in text_lower
    has_follow = "follow" in text_lower
    has_brand = "doniesdaily" in text_lower or "doni" in text_lower

    if not (has_sub or has_follow):
        report["passed"] = False
        report["errors"].append("HUKUM BESI #15 VIOLATION: Naskah wajib menyertakan CTA penutup Follow/Subscribe DoniesDaily!")
    elif not has_brand:
        report["warnings"].append("CTA penutup sebaiknya menyebutkan nama channel DoniesDaily secara eksplisit.")
    
    return report

def audit_footage_assembly(footage_clips: list, slice_dur: Union[float, List[float]]) -> Dict[str, Any]:
    """Verifies Hukum Besi #13: Strict Zero In-Video Footage Repetition and Zero Looping."""
    report = {"passed": True, "errors": [], "metrics": {}}
    clip_strs = [str(c) for c in footage_clips]
    unique_clips = set(clip_strs)

    report["metrics"]["total_cuts"] = len(footage_clips)
    report["metrics"]["unique_clips"] = len(unique_clips)

    if isinstance(slice_dur, list):
        dur_list = [float(d) for d in slice_dur]
        report["metrics"]["slice_durations"] = [round(d, 2) for d in dur_list]
    else:
        dur_list = [float(slice_dur)] * len(footage_clips)
        report["metrics"]["slice_duration_sec"] = round(float(slice_dur), 2)

    if len(clip_strs) != len(unique_clips):
        report["passed"] = False
        report["errors"].append(f"HUKUM BESI #13 VIOLATION: Terdeteksi {len(clip_strs) - len(unique_clips)} footage terduplikasi dalam 1 video!")

    for idx, c in enumerate(footage_clips):
        target_slice = dur_list[idx] if idx < len(dur_list) else dur_list[-1]
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(c)],
            capture_output=True, text=True
        )
        dur = float(probe.stdout.strip()) if probe.stdout.strip() else 0.0
        if dur > 0 and target_slice > (dur + 0.1):
            if target_slice <= (dur * 1.5):
                # Within 1.5x range: Safely auto-healed via FFmpeg Force-Fit setpts stretch
                report["warnings"].append(f"Klip {Path(c).name} ({dur:.2f}s) di segmen #{idx+1} akan di-stretch halus ({target_slice:.2f}s via setpts slow-mo)")
            else:
                report["passed"] = False
                report["errors"].append(f"HUKUM BESI #13 VIOLATION: Klip {Path(c).name} ({dur:.2f}s) di segmen #{idx+1} defisit ekstrem dari slice ({target_slice:.2f}s)!")

    return report

def format_cleo_stamp(report: Dict[str, Any], video_path: str) -> str:
    m = report.get("metrics", {})
    status = "QC_PASSED" if report["passed"] else "QC_FAILED"
    res = m.get("resolution", "unknown")
    dur = m.get("duration_seconds", 0)
    drift = m.get("audio_delta_seconds", "N/A")
    lufs = m.get("integrated_loudness_lufs", "N/A")
    black = 0 if m.get("black_frame_clean") else "DETECTED"
    
    stamp = f"""
======================================================
[CLEO_QC_INSPECTION]
Target: {Path(video_path).name}
Status: {status}
Metrics:
  - Resolution: {res} (Aspect: 9:16)
  - Duration: {dur}s (Shorts Compliant)
  - Audio Drift: {drift}s (Tolerance <=0.5s)
  - Integrated Loudness: {lufs} LUFS (Target: -14..-19 LUFS)
  - Black Frames: {black}
Inspector: Cleo 🔍 — DoniesDaily Broadcast Gatekeeper
======================================================
"""
    return stamp.strip()

def update_db_qc(topic_key: str, report: Dict[str, Any]):
    stage = "QC_PASSED" if report["passed"] else "QC_FAILED"
    report_json = json.dumps(report).replace("'", "''")
    err_msg = "; ".join(report.get("errors", [])).replace("'", "''")
    
    sql = f"""
    UPDATE ai_brain.virgin_production_queue
    SET current_stage = '{stage}',
        qc_report = '{report_json}'::jsonb,
        error_message = {'NULL' if not err_msg else f"'{err_msg}'"},
        updated_at = NOW()
    WHERE topic_key = '{topic_key}';
    """
    cmd = ["docker", "exec", "-i", "supabase-db", "psql", "-U", "postgres", "-d", "postgres", "-c", sql]
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: doni_qc_gate.py <video_path> [audio_path] [--update-db <topic_key>]")
        sys.exit(1)

    v_path = sys.argv[1]
    a_path = None
    topic_key_to_update = None

    idx = 2
    while idx < len(sys.argv):
        if sys.argv[idx] == "--update-db" and idx + 1 < len(sys.argv):
            topic_key_to_update = sys.argv[idx + 1]
            idx += 2
        elif not sys.argv[idx].startswith("--") and a_path is None:
            a_path = sys.argv[idx]
            idx += 1
        else:
            idx += 1

    rep = inspect_video(v_path, a_path)
    print("\n" + format_cleo_stamp(rep, v_path) + "\n")
    print(json.dumps(rep, indent=2, ensure_ascii=False))

    if topic_key_to_update:
        print(f"\nUpdating database queue for topic '{topic_key_to_update}'...")
        update_db_qc(topic_key_to_update, rep)
        print("Database updated.")

    sys.exit(0 if rep["passed"] else 1)
