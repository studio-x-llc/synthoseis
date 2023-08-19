"""
Docker entrypoint
"""

import boto3
import logging
import numpy as np
import os
from pathlib import Path

from synthoseis.main import build_model


def create_factor_dict():
    factor_dict = dict()
    factor_dict["layershiftsamples"] = int(np.random.triangular(35, 75, 125))
    factor_dict["RPshiftsamples"] = int(np.random.triangular(5, 11, 20))
    factor_dict["shalerho_factor"] = 1.0
    factor_dict["shalevp_factor"] = 1.0
    factor_dict["shalevs_factor"] = 1.0
    factor_dict["sandrho_factor"] = 1.0
    factor_dict["sandvp_factor"] = 1.0
    factor_dict["sandvs_factor"] = 1.0
    # Amplitude scaling factors for n, m ,f volumes
    factor_dict["nearfactor"] = 1.0
    factor_dict["midfactor"] = 1.0
    factor_dict["farfactor"] = 1.0


def main() -> None:
    data_home = Path.home() / "synthoseis"
    data_home.mkdir(parents=True, exist_ok=True)
    result_home = data_home / "results"
    result_home.mkdir(parents=True, exist_ok=True)

    config_bucket = os.environ.get("CONFIG_BUCKET")
    config_key = os.environ.get("CONFIG_KEY")
    run_id = os.environ.get("RUN_ID", "test")
    result_bucket = os.environ.get("RESULT_BUCKET")
    result_prefix = os.environ.get("RESULT_PREFIX")

    s3 = boto3.client("s3")

    if config_bucket is None or config_key is None:
        config_path = Path("/opt/synthoseis/defaults/example.json")
        logging.info(f"Using the default config at {str(config_path)}")
    else:
        config = s3.get_object(Bucket=config_bucket, Key=config_key)["Body"].read().decode()
        config_path = data_home / "userconfig.json"

        with open(config_path, "w") as f:
            f.write(config)

    s3 = boto3.client("s3")

    build_model(
        user_json=str(config_path),
        run_id=run_id,
        rpm_factors=create_factor_dict(),
        project_folder=str(result_home),
    )

    if result_bucket is not None and result_prefix is not None:
        # Upload all files saved to the project directory
        for p in result_home.rglob("*"):
            key = str(p.relative_to(result_home))
            s3.upload_file(
                Filename=str(p),
                Bucket=result_bucket,
                Key=result_prefix + "/" + key
            )
    else:
        logging.info("Skippping result export due to missing RESULT_BUCKET or RESULT_PREFIX")


if __name__ == "__main__":
    main()
