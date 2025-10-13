import speedtest

def format_speedtest_results():
    """
    Performs a Speed Test, automatically selecting the optimal server 
    (based on ping/latency). Prints results to stdout and returns a dict.
    """
    try:
        import speedtest
    except Exception as e:
        print(f"[Import Error] cannot import speedtest: {e}")
        return None

    def bps_to_mbps(b): 
        try:
            return round(b / 1_000_000, 2)
        except Exception:
            return None

    print("--- STARTING SPEED TEST ---")
    print("1. Searching for available servers...")
    st = speedtest.Speedtest()

    print("2. Selecting best server...")
    best = st.get_best_server()
    sponsor = best.get("sponsor", "")
    host = best.get("host", "")
    country = best.get("country", "")
    latency = best.get("latency", "n/a")
    print(f"Best server: {sponsor} ({host}) - {country} - latency: {latency} ms")

    print("3. Starting Download speed measurement...")
    download_bps = st.download()

    print("4. Starting Upload speed measurement...")
    upload_bps = st.upload()

    # Try to get ping/result info if available
    results = {}
    try:
        results = st.results.dict() if hasattr(st, "results") else {}
    except Exception:
        results = {}

    ping = results.get("ping") if isinstance(results, dict) else None
    try:
        client_info = st.get_config().get("client", {})
    except Exception:
        client_info = {}

    # Print nicely
    print("\n=== SPEEDTEST RESULTS ===")
    print(f"Download : {bps_to_mbps(download_bps)} Mbps ({int(download_bps)} bps)")
    print(f"Upload   : {bps_to_mbps(upload_bps)} Mbps ({int(upload_bps)} bps)")
    print(f"Ping     : {ping if ping is not None else latency} ms")
    if client_info:
        print(f"Your IP  : {client_info.get('ip','')}, ISP: {client_info.get('isp','')}")
        print(f"Location : {client_info.get('lat','')},{client_info.get('lon','')}")
    print(f"Server   : {sponsor} - {host} ({country})")
    print("=========================\n")

    return {
        "download_bps": download_bps,
        "upload_bps": upload_bps,
        "download_mbps": bps_to_mbps(download_bps),
        "upload_mbps": bps_to_mbps(upload_bps),
        "ping_ms": ping if ping is not None else latency,
        "server": best,
        "client": client_info,
        "raw_results": results
    }
