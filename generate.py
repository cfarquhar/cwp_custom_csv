import csv
import os
import requests
import time
import urllib3

from functools import reduce
from json.decoder import JSONDecodeError

# e.g. https://us-east1.cloud.twistlock.com/us-1-123456789
CWP_API = f"{os.environ.get('TWISTLOCK_ADDRESS')}/api/v1"

CWP_USER = os.environ.get("TWISTLOCK_USER")
CWP_PASSWORD = os.environ.get("TWISTLOCK_PASSWORD")

PAGE_SIZE = 50
RETRY_LIMIT = 10
VERIFY_TLS = not os.environ.get("TLS_INSECURE", False)


class CwpApi:
    def __init__(self, endpoint, user, password):
        self.endpoint = endpoint
        self.user = user
        self.password = password
        self.token = ""
        self.verify_tls = VERIFY_TLS

        # Avoid cluttering output if TLS verify is False
        if not self.verify_tls:
            urllib3.disable_warnings()

        self._get_token()

    def _get_token(self):
        body = {"username": self.user, "password": self.password}
        r = requests.post(
            f"{self.endpoint}/authenticate", json=body, verify=self.verify_tls
        )
        if r.status_code != 200:
            raise Exception(
                f"Unable to authenticate to {CWP_API} with provided credentials."
            )
        self.token = r.json()["token"]

    def _get_api(self, url, headers, params):
        r = requests.get(
            url, headers=headers, params=params, verify=self.verify_tls
        )
        return r

    def get_all(self, api_path, params={}):
        retries = 0
        finished = False
        results = []

        params["offset"] = 0
        params["limit"] = PAGE_SIZE

        headers = {
            "Authorization": f"Bearer {self.token}",
        }

        while not finished and retries < RETRY_LIMIT:
            r = self._get_api(
                url=f"{self.endpoint}/{api_path}", headers=headers, params=params
            )

            try:
                result_count = len(r.json())
            except (JSONDecodeError, TypeError):
                result_count = 0

            if r.status_code == 401:
                self._get_token()
                headers = {"Authorization": f"Bearer {self.token}"}
            elif r.status_code != 200:
                time.sleep(5)
                retries += 1
            else:
                retries = 0
                if result_count == 0:
                    finished = True
                else:
                    params["offset"] += PAGE_SIZE
            try:
                results += r.json()
            except TypeError:
                pass

        return results


output_map = [
    {
        "filename": "hosts.csv",
        "endpoint": "hosts",
        "params": {},
        "fields": [
            {"alias": "hostname", "path": ["hostname"]},
            {"alias": "osDistro", "path": ["osDistro"]},
            {"alias": "osDistroVersion", "path": ["osDistroVersion"]},
            {"alias": "osDistroRelease", "path": ["osDistroRelease"]},
            {"alias": "CSP", "path": ["cloudMetadata", "provider"]},
            {"alias": "CSP Account", "path": ["cloudMetadata", "accountID"]},
        ],
    },
    {
        "filename": "containers.csv",
        "endpoint": "containers",
        "params": {},
        "fields": [
            {"alias": "container name", "path": ["info", "name"]},
            {"alias": "image", "path": ["info", "image"]},
            {"alias": "hostname", "path": ["hostname"]},
            {"alias": "cluster", "path": ["info", "cluster"]},
            {"alias": "namespace", "path": ["info", "namespace"]},
            {"alias": "CSP", "path": ["info", "cloudMetadata", "provider"]},
            {"alias": "CSP Account", "path": ["info", "cloudMetadata", "accountID"]},
        ],
    },
]

if __name__ == "__main__":
    api = CwpApi(CWP_API, CWP_USER, CWP_PASSWORD)
    for output in output_map:
        results = api.get_all(output["endpoint"], output["params"])

        with open(output["filename"], "w", newline="") as f:
            writer = csv.writer(f)
            header = [f["alias"] for f in output["fields"]]
            writer.writerow(header)
            
            for result in results:
                row = []
                for field in output["fields"]:
                    row.append(
                        reduce(
                            lambda d, key: d.get(key) if d else None,
                            field["path"],
                            result,
                        )
                    )
                writer.writerow(row)
