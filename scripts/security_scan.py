#!/usr/bin/env python3
"""
Run comprehensive security scans.

This script runs security audits on all project dependencies
(NPM and Python) and generates a security report.

Usage:
    python scripts/security_scan.py [--output FILE] [--format FORMAT]

Examples:
    python scripts/security_scan.py
    python scripts/security_scan.py --output security-report.json
    python scripts/security_scan.py --format markdown --output security-report.md
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List


def _extract_npm_vulnerability_total(audit_data: dict) -> int:
    """Normalize npm audit vulnerability counts across npm output formats."""
    vulnerabilities = audit_data.get("metadata", {}).get("vulnerabilities", 0)
    if isinstance(vulnerabilities, int):
        return vulnerabilities
    if isinstance(vulnerabilities, dict):
        return sum(value for value in vulnerabilities.values() if isinstance(value, int))
    return 0


def _python_dependency_manifest() -> Path | None:
    """Return the Python dependency manifest used for auditing."""
    requirements = Path("requirements.txt")
    return requirements if requirements.exists() else None


def _count_python_vulnerabilities(results: list | dict) -> int:
    """Count actual Python vulnerabilities, excluding scanner errors."""
    if isinstance(results, list):
        return sum(1 for item in results if isinstance(item, dict) and "error" not in item)
    return 0


def run_command(cmd: List[str], cwd: Path = None, timeout: int = 60) -> dict:
    """
    Run a command and capture output.

    Args:
        cmd: Command and arguments as list
        cwd: Working directory
        timeout: Timeout in seconds

    Returns:
        Dict with stdout, stderr, returncode
    """
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": f"Command timed out after {timeout}s", "returncode": -1}
    except FileNotFoundError as e:
        return {"stdout": "", "stderr": f"Command not found: {e}", "returncode": -2}


def npm_audit(path: Path) -> dict:
    """
    Run npm audit in directory.

    Args:
        path: Directory containing package.json

    Returns:
        Audit results
    """
    if not (path / "package.json").exists():
        return {"error": "No package.json found", "vulnerabilities": 0}

    result = run_command(["npm", "audit", "--json"], cwd=path)

    if result["returncode"] != 0:
        # npm audit returns non-zero if vulnerabilities found
        if result["stdout"]:
            try:
                data = json.loads(result["stdout"])
                return {
                    "vulnerabilities": _extract_npm_vulnerability_total(data),
                    "details": data,
                    "has_vulnerabilities": True,
                }
            except json.JSONDecodeError:
                pass

    if result["stdout"]:
        try:
            data = json.loads(result["stdout"])
            return {
                "vulnerabilities": _extract_npm_vulnerability_total(data),
                "details": data,
                "has_vulnerabilities": False,
            }
        except json.JSONDecodeError:
            pass

    return {"error": result["stderr"] or "Unknown error", "vulnerabilities": 0}


def pip_safety() -> list:
    """
    Run safety check on Python dependencies.

    Returns:
        List of vulnerabilities found
    """
    # Try safety first
    result = run_command(["safety", "check", "--json"])

    if result["returncode"] == 0 and result["stdout"]:
        try:
            return json.loads(result["stdout"])
        except json.JSONDecodeError:
            pass

    # Fallback to pip-audit
    requirements = _python_dependency_manifest()
    if requirements is None:
        return [{"error": "No requirements.txt found for pip-audit"}]

    result = run_command(["pip-audit", "-r", str(requirements), "-f", "json"])

    if result["stdout"]:
        try:
            return json.loads(result["stdout"])
        except json.JSONDecodeError:
            pass

    return [{"error": "No Python security scanner available or requirements.txt not found"}]


def bandit_scan(path: Path) -> dict:
    """
    Run bandit security lint on Python code.

    Args:
        path: Root directory to scan

    Returns:
        Bandit results
    """
    python_dirs = ["conductor-core/src", "conductor-gemini/src", "scripts"]
    results = {}

    for py_dir in python_dirs:
        py_path = path / py_dir
        if py_path.exists():
            result = run_command(["bandit", "-r", str(py_path), "-f", "json"], timeout=120)

            if result["stdout"]:
                try:
                    data = json.loads(result["stdout"])
                    results[py_dir] = {
                        "issues": len(data.get("results", [])),
                        "severity_counts": data.get("results", [])
                        and {
                            "HIGH": sum(1 for i in data["results"] if i.get("issue_severity") == "HIGH"),
                            "MEDIUM": sum(1 for i in data["results"] if i.get("issue_severity") == "MEDIUM"),
                            "LOW": sum(1 for i in data["results"] if i.get("issue_severity") == "LOW"),
                        }
                        or {},
                    }
                except json.JSONDecodeError:
                    results[py_dir] = {"error": "Failed to parse bandit output"}

    return results


def generate_report(
    npm_results: Dict[str, dict], python_results: list, bandit_results: dict, output_file: Path, format: str = "json"
):
    """
    Generate security report.

    Args:
        npm_results: NPM audit results by directory
        python_results: Python safety results
        bandit_results: Bandit scan results
        output_file: Output file path
        format: Output format (json, markdown, text)
    """
    report = {
        "scanned_at": datetime.now().isoformat(),
        "npm": npm_results,
        "python": python_results,
        "bandit": bandit_results,
        "summary": {
            "total_npm_vulnerabilities": sum(r.get("vulnerabilities", 0) for r in npm_results.values()),
            "total_python_vulnerabilities": _count_python_vulnerabilities(python_results),
            "total_bandit_issues": sum(
                r.get("issues", 0) for r in bandit_results.values() if isinstance(r, dict) and "error" not in r
            ),
        },
    }

    if format == "json":
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

    elif format == "markdown":
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("# Security Scan Report\n\n")
            f.write(f"**Generated:** {report['scanned_at']}\n\n")

            f.write("## Summary\n\n")
            f.write("| Scanner | Vulnerabilities |\n")
            f.write("|---------|----------------|\n")
            f.write(f"| NPM | {report['summary']['total_npm_vulnerabilities']} |\n")
            f.write(f"| Python | {report['summary']['total_python_vulnerabilities']} |\n")
            f.write(f"| Bandit | {report['summary']['total_bandit_issues']} |\n\n")

            if npm_results:
                f.write("## NPM Audits\n\n")
                for dir, result in npm_results.items():
                    status = "[ERROR]" if result.get("has_vulnerabilities") else "[OK]"
                    vulns = result.get("vulnerabilities", 0)
                    f.write(f"### {dir} {status}\n\n")
                    f.write(f"Vulnerabilities: {vulns}\n\n")
                    if "error" in result:
                        f.write(f"Error: {result['error']}\n\n")

            if python_results:
                f.write("## Python Dependencies\n\n")
                if isinstance(python_results, list) and python_results:
                    f.write(f"Vulnerabilities found: {len(python_results)}\n\n")
                    for vuln in python_results[:10]:  # Show first 10
                        if isinstance(vuln, dict):
                            f.write(f"- {vuln.get('package_name', 'Unknown')}: {vuln.get('vuln_id', 'Unknown')}\n")
                    if len(python_results) > 10:
                        f.write(f"\n... and {len(python_results) - 10} more\n")

            if bandit_results:
                f.write("## Bandit Security Lint\n\n")
                for dir, result in bandit_results.items():
                    if isinstance(result, dict) and "error" not in result:
                        f.write(f"### {dir}\n\n")
                        f.write(f"Issues: {result.get('issues', 0)}\n")
                        if result.get("severity_counts"):
                            f.write(f"- HIGH: {result['severity_counts'].get('HIGH', 0)}\n")
                            f.write(f"- MEDIUM: {result['severity_counts'].get('MEDIUM', 0)}\n")
                            f.write(f"- LOW: {result['severity_counts'].get('LOW', 0)}\n\n")

    elif format == "text":
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("Security Scan Report\n")
            f.write(f"Generated: {report['scanned_at']}\n\n")
            f.write("Summary:\n")
            f.write(f"  NPM Vulnerabilities: {report['summary']['total_npm_vulnerabilities']}\n")
            f.write(f"  Python Vulnerabilities: {report['summary']['total_python_vulnerabilities']}\n")
            f.write(f"  Bandit Issues: {report['summary']['total_bandit_issues']}\n")

    return report


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run comprehensive security scans",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--output", type=Path, default=None, help="Output file (default: .conductor/security-report.json)"
    )

    parser.add_argument(
        "--format", choices=["json", "markdown", "text"], default="json", help="Output format (default: json)"
    )

    parser.add_argument("--no-bandit", action="store_true", help="Skip bandit security lint")

    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    # Set up output
    if args.output:
        output_file = args.output
    else:
        output_dir = Path(".conductor")
        output_dir.mkdir(parents=True, exist_ok=True)
        ext = {"json": "json", "markdown": "md", "text": "txt"}[args.format]
        output_file = output_dir / f"security-report.{ext}"

    root_dir = Path(__file__).parent.parent

    print("[SECURITY] Starting security scan...")
    print(f"Output: {output_file}")
    print()

    # NPM audits
    print("Running NPM audits...")
    npm_dirs = ["mcp-server", "conductor-vscode", "mcp"]
    npm_results = {}

    for npm_dir in npm_dirs:
        npm_path = root_dir / npm_dir
        if npm_path.exists():
            print(f"  Scanning {npm_dir}...")
            npm_results[npm_dir] = npm_audit(npm_path)
            vulns = npm_results[npm_dir].get("vulnerabilities", 0)
            status = "[ERROR]" if vulns > 0 else "[OK]"
            print(f"    {status} {vulns} vulnerabilities")

    # Python safety
    print("\nRunning Python dependency check...")
    python_results = pip_safety()
    vulns = _count_python_vulnerabilities(python_results)
    status = "[ERROR]" if vulns > 0 else "[OK]"
    print(f"  {status} {vulns} vulnerabilities")

    # Bandit scan
    bandit_results = {}
    if not args.no_bandit:
        print("\nRunning Bandit security lint...")
        bandit_results = bandit_scan(root_dir)
        for dir, result in bandit_results.items():
            if isinstance(result, dict) and "error" not in result:
                issues = result.get("issues", 0)
                status = "[ERROR]" if issues > 0 else "[OK]"
                print(f"  {status} {dir}: {issues} issues")
    else:
        print("\n[SKIP]  Skipping Bandit scan (--no-bandit)")

    # Generate report
    print("\nGenerating report...")
    report = generate_report(npm_results, python_results, bandit_results, output_file, args.format)

    # Summary
    print("\n[SUMMARY] Security Scan Summary:")
    print(f"   NPM: {report['summary']['total_npm_vulnerabilities']} vulnerabilities")
    print(f"   Python: {report['summary']['total_python_vulnerabilities']} vulnerabilities")
    print(f"   Bandit: {report['summary']['total_bandit_issues']} issues")
    print(f"\n[OK] Security scan complete! Report: {output_file}")

    # Exit with error if vulnerabilities found
    total_vulns = report["summary"]["total_npm_vulnerabilities"] + report["summary"]["total_python_vulnerabilities"]

    if total_vulns > 0:
        print(f"\n[WARNING]  {total_vulns} security vulnerabilities detected!")
        if args.format == "json":
            print(f"   Review: {output_file}")
        sys.exit(1)
    else:
        print("\n[OK] No security vulnerabilities detected!")


if __name__ == "__main__":
    main()
