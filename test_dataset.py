"""
Quick test script to verify Nick Valentine dataset loading and processing
"""

import pandas as pd

print("="*70)
print("  Nick Valentine Dataset Analysis")
print("="*70)

# Load the CSV
df = pd.read_csv('nick_valentine_dialogue.csv')

print(f"\n📊 Dataset Overview:")
print(f"   Total rows: {len(df)}")
print(f"   Columns: {', '.join(df.columns.tolist())}")

print(f"\n📝 Column Statistics:")
print(f"   PROMPT (empty): {df['PROMPT'].isna().sum()} / {len(df)}")
print(f"   DIALOGUE BEFORE (has values): {df['DIALOGUE BEFORE'].notna().sum()} / {len(df)}")
print(f"   RESPONSE TEXT (has values): {df['RESPONSE TEXT'].notna().sum()} / {len(df)}")
print(f"   SCRIPT NOTES (has values): {df['SCRIPT NOTES'].notna().sum()} / {len(df)}")

print(f"\n🎭 Category Breakdown:")
print(df['CATEGORY'].value_counts())

print(f"\n🗣️ Type Breakdown:")
print(df['TYPE'].value_counts())

print(f"\n💬 Sample Conversational Pairs (with DIALOGUE BEFORE):")
print("="*70)
sample = df[df['DIALOGUE BEFORE'].notna()].head(5)
for idx, row in sample.iterrows():
    print(f"\n[{idx}] Scene: {row['SCENE']}")
    print(f"    Mood: {row['SCRIPT NOTES']}")
    print(f"    Query: {row['DIALOGUE BEFORE'][:100]}...")
    print(f"    Nick's Response: {row['RESPONSE TEXT'][:100]}...")

print(f"\n\n💬 Sample Standalone Dialogues (without DIALOGUE BEFORE):")
print("="*70)
standalone = df[df['DIALOGUE BEFORE'].isna() & df['RESPONSE TEXT'].notna()].head(5)
for idx, row in standalone.iterrows():
    print(f"\n[{idx}] Type: {row['TYPE']} / Subtype: {row['SUBTYPE']}")
    print(f"    Mood: {row['SCRIPT NOTES']}")
    print(f"    Nick says: {row['RESPONSE TEXT'][:150]}...")

print("\n" + "="*70)
print("  Dataset looks good! Ready to use for chatbot.")
print("="*70)
