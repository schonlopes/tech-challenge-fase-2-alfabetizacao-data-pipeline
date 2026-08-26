from pathlib import Path

from alfabetizacao_pipeline.sample_data import generate_sample_data


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    counts = generate_sample_data(project_root / "data" / "sample")
    print("Amostra sintetica gerada:")
    for name, count in counts.items():
        print(f"- {name}: {count} linhas")

