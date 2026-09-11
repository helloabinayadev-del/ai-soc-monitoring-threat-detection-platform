import React, { useState, useEffect } from 'react';
import { ThreatIntel } from '../types';
import { threatIntelApi } from '../services/api';
import { Globe2, Search, Plus, ShieldAlert, CheckCircle } from 'lucide-react';

export const ThreatIntelPage: React.FC = () => {
  const [intelList, setIntelList] = useState<ThreatIntel[]>([]);
  const [searchIoc, setSearchIoc] = useState('');
  const [lookupResult, setLookupResult] = useState<ThreatIntel | null>(null);
  const [lookupError, setLookupError] = useState('');
  const [loading, setLoading] = useState(true);

  // New IOC Form State
  const [iocVal, setIocVal] = useState('');
  const [iocType, setIocType] = useState<'IP' | 'MD5' | 'SHA256' | 'DOMAIN' | 'URL'>('IP');
  const [threatType, setThreatType] = useState('Command & Control');
  const [score, setScore] = useState(85);
  const [isAddOpen, setIsAddOpen] = useState(false);

  const fetchIntel = async () => {
    try {
      const data = await threatIntelApi.getThreatIntel();
      setIntelList(data);
    } catch (e) {
      console.error('[!] Threat Intel fetch failed:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIntel();
  }, []);

  const [cveResult, setCveResult] = useState<any>(null);

  const handleLookup = async (e: React.FormEvent) => {
    e.preventDefault();
    setLookupError('');
    setLookupResult(null);
    setCveResult(null);
    if (!searchIoc.trim()) return;

    const term = searchIoc.trim();
    if (term.toUpperCase().startsWith('CVE-')) {
      try {
        const res = await threatIntelApi.lookupCve(term);
        setCveResult(res);
      } catch (err) {
        setLookupError(`No matching CVE record found for ${term}.`);
      }
    } else {
      try {
        const res = await threatIntelApi.lookupIoc(term);
        setLookupResult(res);
      } catch (err) {
        setLookupError('No matching Indicator of Compromise (IOC) found in active threat feeds.');
      }
    }
  };

  const handleAddIoc = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await threatIntelApi.addIoc({
        ioc_value: iocVal,
        ioc_type: iocType,
        threat_type: threatType,
        threat_score: score,
        source_feed: 'Custom Analyst IOC Feed',
        description: 'Manually ingested IOC indicator',
      });
      setIocVal('');
      setIsAddOpen(false);
      fetchIntel();
    } catch (err) {
      console.error('[!] Failed to insert IOC indicator:', err);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Globe2 className="h-5 w-5 text-cyan-400" />
            Threat Intelligence & Indicator Feeds (IOC)
          </h2>
          <p className="text-xs text-slate-400 font-mono">
            AlienVault OTX, AbuseIPDB, VirusTotal, and custom threat indicator lookup database.
          </p>
        </div>

        <button
          onClick={() => setIsAddOpen(!isAddOpen)}
          className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs flex items-center space-x-2 transition shadow-lg shadow-cyan-500/20"
        >
          <Plus className="h-4 w-4" />
          <span>Add Custom IOC</span>
        </button>
      </div>

      {/* Add IOC Form */}
      {isAddOpen && (
        <form onSubmit={handleAddIoc} className="p-4 rounded-xl border border-cyan-800 bg-soc-card space-y-3 font-mono text-xs">
          <div className="font-semibold text-cyan-400">INGEST NEW INDICATOR OF COMPROMISE (IOC)</div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label htmlFor="add-ioc-val" className="block text-slate-400 mb-1">IOC VALUE</label>
              <input
                id="add-ioc-val"
                name="iocVal"
                type="text"
                required
                autoComplete="off"
                value={iocVal}
                onChange={(e) => setIocVal(e.target.value)}
                placeholder="198.51.100.45 or MD5 hash..."
                className="w-full bg-soc-bg border border-soc-border rounded p-2 text-slate-100"
              />
            </div>
            <div>
              <label htmlFor="add-ioc-type" className="block text-slate-400 mb-1">IOC TYPE</label>
              <select
                id="add-ioc-type"
                name="iocType"
                value={iocType}
                onChange={(e: any) => setIocType(e.target.value)}
                className="w-full bg-soc-bg border border-soc-border rounded p-2 text-slate-100"
              >
                <option value="IP">IP Address</option>
                <option value="MD5">MD5 Hash</option>
                <option value="SHA256">SHA256 Hash</option>
                <option value="DOMAIN">Domain</option>
                <option value="URL">URL</option>
              </select>
            </div>
            <div>
              <label htmlFor="add-ioc-score" className="block text-slate-400 mb-1">THREAT SCORE (0-100)</label>
              <input
                id="add-ioc-score"
                name="score"
                type="number"
                min="0"
                max="100"
                autoComplete="off"
                value={score}
                onChange={(e) => setScore(Number(e.target.value))}
                className="w-full bg-soc-bg border border-soc-border rounded p-2 text-slate-100"
              />
            </div>
          </div>
          <div className="flex justify-end space-x-2">
            <button type="button" onClick={() => setIsAddOpen(false)} className="px-3 py-1.5 rounded bg-slate-800 text-slate-300">Cancel</button>
            <button type="submit" className="px-4 py-1.5 rounded bg-cyan-600 text-white font-bold">Add Indicator</button>
          </div>
        </form>
      )}

      {/* Live Threat Lookup Box */}
      <div className="p-5 rounded-xl border border-soc-border bg-soc-card/90 glass-panel space-y-3">
        <h3 className="font-semibold text-xs text-slate-300 font-mono uppercase tracking-wider">
          Real-Time Threat Intel Lookup
        </h3>
        <form onSubmit={handleLookup} className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
            <input
              id="intel-search-input"
              name="searchIoc"
              type="text"
              autoComplete="off"
              aria-label="Query IP address, file hash, or domain against Threat Intel database"
              value={searchIoc}
              onChange={(e) => setSearchIoc(e.target.value)}
              placeholder="Query IP address, file hash, or domain against Threat Intel database..."
              className="w-full pl-9 pr-4 py-2 text-xs font-mono bg-soc-bg border border-soc-border rounded-lg text-slate-100 focus:outline-none focus:border-cyan-500"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs font-mono transition"
          >
            Lookup IOC
          </button>
        </form>

        {lookupResult && (
          <div className="p-4 rounded-lg bg-red-950/40 border border-red-800 font-mono text-xs space-y-2 text-slate-200">
            <div className="flex items-center space-x-2 text-red-400 font-bold">
              <ShieldAlert className="h-4 w-4" />
              <span>MALICIOUS MATCH DETECTED</span>
            </div>
            <div>IOC Value: <span className="text-cyan-400">{lookupResult.ioc_value}</span> ({lookupResult.ioc_type})</div>
            <div>Threat Type: {lookupResult.threat_type} | Threat Score: <span className="text-red-400 font-bold">{lookupResult.threat_score}/100</span></div>
            <div>Source Feed: {lookupResult.source_feed}</div>
            <div className="text-slate-400">{lookupResult.description}</div>
          </div>
        )}

        {cveResult && (
          <div className="p-4 rounded-lg bg-purple-950/40 border border-purple-800 font-mono text-xs space-y-2 text-slate-200">
            <div className="flex items-center space-x-2 text-purple-300 font-bold">
              <ShieldAlert className="h-4 w-4 text-purple-400" />
              <span>NVD / MITRE CVE VULNERABILITY RECORD</span>
            </div>
            <div>CVE Identifier: <span className="text-cyan-400 font-bold">{cveResult.cve_id}</span> | CVSS Score: <span className="text-red-400 font-bold">{cveResult.cvss_score} / 10</span> ({cveResult.severity})</div>
            <div className="font-sans font-semibold text-slate-100">{cveResult.title}</div>
            <div className="text-slate-300">{cveResult.description}</div>
            <div className="text-cyan-300">Remediation: {cveResult.remediation}</div>
          </div>
        )}

        {lookupError && (
          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-slate-400">
            {lookupError}
          </div>
        )}
      </div>

      {/* Threat Feeds Table */}
      <div className="overflow-x-auto rounded-xl border border-soc-border bg-soc-card/90">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-soc-bg/80 text-slate-400 font-mono text-[11px] uppercase tracking-wider border-b border-soc-border">
            <tr>
              <th className="py-3 px-4">IOC Value</th>
              <th className="py-3 px-4">Type</th>
              <th className="py-3 px-4">Threat Type</th>
              <th className="py-3 px-4">Threat Score</th>
              <th className="py-3 px-4">Feed Provider</th>
              <th className="py-3 px-4">Description</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-soc-border font-mono">
            {intelList.map((item) => (
              <tr key={item.id} className="hover:bg-soc-hover/80 transition">
                <td className="py-3 px-4 font-bold text-cyan-400">{item.ioc_value}</td>
                <td className="py-3 px-4 text-slate-400">{item.ioc_type}</td>
                <td className="py-3 px-4 text-slate-200">{item.threat_type || 'N/A'}</td>
                <td className="py-3 px-4">
                  <span className="px-2 py-0.5 rounded bg-red-950 text-red-400 border border-red-800 font-bold">
                    {item.threat_score} / 100
                  </span>
                </td>
                <td className="py-3 px-4 text-slate-400">{item.source_feed}</td>
                <td className="py-3 px-4 text-slate-300">{item.description || 'N/A'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
