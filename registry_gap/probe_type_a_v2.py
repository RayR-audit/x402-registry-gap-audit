# Type A probe v2: extract ONLY the recipient (settlement payee) from decoded 402 challenge.
# v1 counted currency contracts as addresses -- inflated. This is the corrected version.
import urllib.request, urllib.error, json, base64, re, time, csv, os

PROXY = {'http': os.environ.get('X402_PROXY', ''), 'https': os.environ.get('X402_PROXY', '')}
opener = urllib.request.build_opener(urllib.request.ProxyHandler(PROXY))
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0')]

REG_CSV = 'data/base_facilitators.csv'
SRC = 'data/csoai_x402_conformance_snapshot_20260927.jsonl'
OUT = 'v4_results_partial.json'

def load_registry():
    return {r['address'].lower() for r in csv.DictReader(open(REG_CSV, encoding='utf-8'))}

def extract_recipient(www):
    """Extract recipient/payTo from WWW-Authenticate challenge. Returns (method, recipient_addr or '')."""
    if not www:
        return '', ''
    method = ''
    if 'method=' in www:
        try:
            method = www.split('method=')[1].split(',')[0].strip('"')
        except Exception:
            pass
    m = re.search(r'request="([^"]+)"', www)
    if m:
        b64 = m.group(1) + '=' * (-len(m.group(1)) % 4)
        try:
            j = json.loads(base64.b64decode(b64))
            # x402 v1: challenges have x402Version/payload/scheme or flat accepts; common key: recipient / payTo
            for key in ('recipient', 'payTo', 'pay_to', 'payee', 'to'):
                if isinstance(j, dict) and key in j and re.match(r'^0x[a-fA-F0-9]{40}$', str(j[key])):
                    return method, str(j[key])
                if isinstance(j, dict) and 'accepts' in j and isinstance(j['accepts'], list):
                    for a in j['accepts']:
                        if isinstance(a, dict):
                            for k2 in ('payTo', 'recipient', 'pay_to', 'to'):
                                if k2 in a and re.match(r'^0x[a-fA-F0-9]{40}$', str(a[k2])):
                                    return method, str(a[k2])
            return method, ''
        except Exception:
            return method, ''
    return method, ''

def probe(url):
    try:
        opener.open(urllib.request.Request(url), timeout=15)
        return {'state': 'NO_402', 'method': '', 'recipient': ''}
    except urllib.error.HTTPError as e:
        if e.code != 402:
            return {'state': 'HTTP_%d' % e.code, 'method': '', 'recipient': ''}
        www = e.headers.get('WWW-Authenticate', '') or ''
        method, recipient = extract_recipient(www)
        return {'state': 'CHALLENGE', 'method': method, 'recipient': recipient}
    except Exception as ex:
        return {'state': 'ERR', 'method': '', 'recipient': ''}

def main():
    reg = load_registry()
    done = set()
    if os.path.exists(OUT):
        done = {r['resource'] for r in csv.DictReader(open(OUT, encoding='utf-8'))}
    rows = [json.loads(l) for l in open(SRC, encoding='utf-8')]
    payable = [r for r in rows if r['state'] == 'PAYABLE']
    newfile = not os.path.exists(OUT)
    with open(OUT, 'a', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        if newfile:
            w.writerow(['resource', 'host', 'probe_state', 'method', 'recipient', 'recipient_in_registry', 'gap_type'])
        for i, r in enumerate(payable):
            if r['resource'] in done:
                continue
            res = probe(r['resource'])
            inreg = '1' if res['recipient'] and res['recipient'].lower() in reg else ('0' if res['recipient'] else '')
            gap = ''
            if res['state'] == 'CHALLENGE':
                if not res['recipient']:
                    gap = 'no_recipient'
                else:
                    gap = 'A_out' if inreg == '0' else 'A_in'
            w.writerow([r['resource'], r['host'], res['state'], res['method'], res['recipient'], inreg, gap])
            f.flush()
            print('%d/%d %s %s %s' % (i+1, len(payable), r['host'][:40], res['state'], gap))
            time.sleep(2)

if __name__ == '__main__':
    main()
