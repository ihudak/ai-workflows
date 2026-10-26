# NVD API Reference

## Endpoint

```
GET https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-XXXX-XXXXX
```

No API key required for low-volume use (rate limit: ~5 req/30 s). Add header `apiKey: <key>` to increase to 50 req/30 s.

## Minimal request (PowerShell)

```powershell
$r = Invoke-RestMethod "https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2023-46604"
$vuln = $r.vulnerabilities[0].cve
```

## Key fields to extract

| Field path | Meaning |
|---|---|
| `$vuln.id` | CVE ID |
| `$vuln.descriptions` | Array of `{lang, value}` — use `lang == "en"` for description |
| `$vuln.configurations[].nodes[].cpeMatch[]` | CPE entries identifying affected software |
| `$vuln.configurations[].nodes[].cpeMatch[].criteria` | CPE URI, e.g. `cpe:2.3:a:apache:activemq:*:*:*:*:*:*:*:*` |
| `$vuln.configurations[].nodes[].cpeMatch[].versionStartIncluding` | Vulnerable from |
| `$vuln.configurations[].nodes[].cpeMatch[].versionEndExcluding` | Fixed in (exclusive upper bound — this is the safe version) |
| `$vuln.configurations[].nodes[].cpeMatch[].versionEndIncluding` | Vulnerable up to and including this version |

## CPE URI structure

```
cpe:2.3:a:<vendor>:<product>:<version>:...
```

- Part `a` = application, `o` = OS, `h` = hardware
- `vendor` and `product` together identify the library (e.g., `apache` / `activemq`, `fasterxml` / `jackson-databind`). The vendor is NVD's name for the publisher, not a Maven groupId: match the product against the artifact, never the vendor against the groupId

## Deriving the safe version

1. Collect all `cpeMatch` entries where `vulnerable == true`.
2. For `versionEndExcluding` (exclusive upper bound): that value **is** the safe version floor.
3. For `versionEndIncluding` (inclusive upper bound, no exclusive upper bound given): the safe floor is one patch above. If the version has a non-numeric suffix (`.Final`, `-RELEASE`, `-RC1`), bump the numeric core and preserve the suffix.

   Examples for non-standard version schemes:
   - `2.14.3.Final` → safe floor: `2.14.4.Final` (Hibernate-style suffix)
   - `1.2.3-RELEASE` → safe floor: `1.2.4-RELEASE` (Spring-style suffix)

4. If multiple ranges exist, do **not** take the highest `versionEndExcluding` across all ranges. Instead, find the range whose `versionStartIncluding`–`versionEndExcluding` window contains the project's current version, and use that range's upper bound as the safe floor. Taking the globally highest bound may push a `5.15.x` project to `5.16.7` when `5.15.16` is the correct fix.

   Example: a project on `5.15.3` with ranges `[5.0.0, 5.15.16)` and `[5.16.0, 5.16.7)` — the matching range is the first one, so the safe floor is `5.15.16`.

## Example: CVE-2023-46604 (Apache ActiveMQ RCE)

```json
{
  "cve": {
    "id": "CVE-2023-46604",
    "descriptions": [{ "lang": "en", "value": "Apache ActiveMQ RCE..." }],
    "configurations": [{
      "nodes": [{
        "cpeMatch": [{
          "vulnerable": true,
          "criteria": "cpe:2.3:a:apache:activemq:*:*:*:*:*:*:*:*",
          "versionStartIncluding": "5.0.0",
          "versionEndExcluding": "5.15.16"
        }, {
          "vulnerable": true,
          "criteria": "cpe:2.3:a:apache:activemq:*:*:*:*:*:*:*:*",
          "versionStartIncluding": "5.16.0",
          "versionEndExcluding": "5.16.7"
        }]
      }]
    }]
  }
}
```

Safe version: by the range holding the current version (step 4 above) — `5.15.16` for a `5.15.x` project, `5.16.7` for a `5.16.x` one, or the latest patch release of that line at or above the bound.

## Fallback: NVD web page

If the API returns no `configurations` (some CVEs lack CPE data), fetch the human-readable page:

```
https://nvd.nist.gov/vuln/detail/<CVE-ID>
```

Use `web_fetch` to retrieve the page and extract the affected software table.

## Maven Central / package registries — finding latest safe version

Once the safe version floor is known, confirm the version exists and find the latest patch in that line:

- **Maven/Gradle**: `https://search.maven.org/solrsearch/select?q=g:<groupId>+AND+a:<artifactId>&core=gav&rows=200&wt=json` (`core=gav` lists one document per version; without it the default core returns one per artifact, carrying only `latestVersion`)
- **npm**: `https://registry.npmjs.org/<package>`  (`.versions` keys list all published versions)
- **PyPI**: `https://pypi.org/pypi/<package>/json`  (`.releases` keys)
- **Go**: `https://proxy.golang.org/<module>/@v/list`
