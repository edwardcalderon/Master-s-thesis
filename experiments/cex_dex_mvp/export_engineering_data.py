"""Export verified compact engineering tables without changing confirmation evidence."""
import argparse
import json
from pathlib import Path
from run import sha256_bytes

HERE=Path(__file__).resolve().parent


def export(run_dir, target):
    metadata=json.loads((run_dir/'run_metadata.json').read_text())
    names=('condition_summary.csv','cell_summary.csv','depth_effects.csv')
    data={name:(run_dir/name).read_bytes() for name in names}
    for name,content in data.items():
        if sha256_bytes(content) != metadata['artifact_sha256'][name]:
            raise ValueError(f'Artifact checksum mismatch: {name}')
    target.mkdir(parents=True,exist_ok=True)
    for name,content in data.items():
        (target/name).write_bytes(content)
    manifest={key:metadata[key] for key in ('run_id','analysis_version','model_version','run_count','seed_range','source_sha256')}
    manifest['files']={name:sha256_bytes(content) for name,content in data.items()}
    manifest['interpretation']='Supplementary synthetic sensitivity; no external validation; cell intervals are descriptive.'
    (target/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'Exported {metadata["run_id"]} to {target}')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir',type=Path,required=True)
    parser.add_argument('--output',type=Path,default=HERE.parent.parent/'thesis/figures/engineering')
    args=parser.parse_args()
    export(args.run_dir,args.output)
