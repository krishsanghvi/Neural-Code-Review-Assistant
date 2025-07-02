#!/usr/bin/env python3
"""Test the code analyzer locally without GitHub"""

from app.models.code_analyzer import SmartCodeAnalyzer
from app.security.vulnerability_scanner import AdvancedSecurityScanner


def test_code_analyzer():
    print("🧪 Testing Smart Code Analyzer...")

    analyzer = SmartCodeAnalyzer()
    security_scanner = AdvancedSecurityScanner()

    # Test code with issues
    test_code = '''
import subprocess
import os

password = "hardcoded_secret_123"

def vulnerable_function(user_input):
    # TODO: Fix this
    print(f"Processing: {user_input}")
    
    if user_input:
        if len(user_input) > 10:
            if user_input.startswith("admin"):
                if ";" in user_input:
                    # SQL injection vulnerability
                    query = "SELECT * FROM users WHERE name = '" + user_input + "'"
                    
                    # Command injection
                    result = subprocess.run(f"cat {user_input}", shell=True)
                    
                    try:
                        dangerous = eval(user_input)
                    except:
                        pass
                    
                    return query, result
    return None
'''

    print("\n🔍 Running code quality analysis...")
    insights = analyzer.analyze_code_quality(test_code, "test.py")

    print(f"Found {len(insights)} insights:")
    for insight in insights:
        severity_emoji = {"warning": "⚠️", "info": "ℹ️", "error": "❌"}
        emoji = severity_emoji.get(insight['severity'], "🔍")
        print(f"  {emoji} [{insight['type']}] {insight['message']}")

    print("\n🔒 Running security analysis...")
    vulnerabilities = security_scanner.scan_for_vulnerabilities(
        test_code, "test.py")

    print(f"Found {len(vulnerabilities)} security issues:")
    for vuln in vulnerabilities:
        severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        emoji = severity_emoji.get(vuln['severity'], "🔍")
        print(f"  {emoji} [{vuln['severity']}] {vuln['description']}")
        print(f"      💡 {vuln['recommendation']}")

    print("\n✅ Test completed!")


if __name__ == "__main__":
    test_code_analyzer()
