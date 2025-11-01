import React, { useEffect, useState } from 'react'
import { listControls, patchControl, getControl, addTextLog, listTextLog, deleteTextLog, listEvidence, uploadEvidence, deleteEvidence, getDashboard, type Control } from './api'

function rowBg(s?: string|null){
  if (s==='MET') return 'bg-green-50'
  if (s==='NOT_MET') return 'bg-red-50'
  if (s==='NA') return 'bg-gray-50'
  return ''
}

const FILTER_INACTIVE = 'bg-gray-50 border-gray-200 hover:bg-gray-100'

type FilterOption = {
  value: string
  label: string
  activeClass: string
}

const C3PAO_FILTERS: FilterOption[] = [
  { value: 'MET', label: 'MET', activeClass: 'bg-green-100 border-green-300 text-green-800' },
  { value: 'NOT_MET', label: 'NOT MET', activeClass: 'bg-red-100 border-red-300 text-red-800' },
  { value: 'NA', label: 'N/A', activeClass: 'bg-gray-100 border-gray-300 text-gray-800' },
  { value: 'UNASSIGNED', label: 'UNASSIGNED', activeClass: 'bg-yellow-100 border-yellow-300 text-yellow-800' },
]

const SELF_IMPL_FILTERS: FilterOption[] = [
  { value: 'Implemented', label: 'Implemented', activeClass: 'bg-green-100 border-green-300 text-green-800' },
  { value: 'Partially Implemented', label: 'Partially Implemented', activeClass: 'bg-yellow-100 border-yellow-300 text-yellow-800' },
  { value: 'Planned or Not Implemented', label: 'Planned or Not Implemented', activeClass: 'bg-red-100 border-red-300 text-red-800' },
  { value: 'Alternative Implementation', label: 'Alternative Implementation', activeClass: 'bg-blue-100 border-blue-300 text-blue-800' },
  { value: 'N/A', label: 'N/A', activeClass: 'bg-gray-100 border-gray-300 text-gray-800' },
  { value: 'UNASSIGNED', label: 'UNASSIGNED', activeClass: 'bg-orange-100 border-orange-300 text-orange-800' },
]

const labelForFilter = (value: string, options: FilterOption[]) => options.find(option => option.value === value)?.label ?? value
const matchesStatus = (value: string | null | undefined, target: string) =>
  ((value ?? 'UNASSIGNED') === target)

export default function App(){
  const [rows, setRows] = useState<Control[]>([])
  const [allRows, setAllRows] = useState<Control[]>([])
  const [q, setQ] = useState('')
  const [domain, setDomain] = useState('')
  const [sel, setSel] = useState<Control|null>(null)
  const [dashboard, setDashboard] = useState<any>(null)
  const [c3paoFilter, setC3paoFilter] = useState<string>('')
  const [implFilter, setImplFilter] = useState<string>('')

  const fetchRows = async() => {
    const data = await listControls(q, domain)
    setAllRows(data)
    applyFilters(data, c3paoFilter, implFilter)
  }

  const fetchDashboard = async() => {
    const data = await getDashboard()
    setDashboard(data)
  }

  const applyFilters = (data: Control[], c3pao: string, impl: string) => {
    let filtered = data
    if (c3pao) {
      filtered = filtered.filter(r => matchesStatus(r.c3pao_finding, c3pao))
    }
    if (impl) {
      filtered = filtered.filter(r => matchesStatus(r.self_impl_status, impl))
    }
    setRows(filtered)
  }

  useEffect(()=>{ 
    fetchRows()
    fetchDashboard()
  },[])
  
  useEffect(()=>{ 
    const t = setTimeout(fetchRows, 250); 
    return ()=>clearTimeout(t) 
  }, [q, domain])

  useEffect(()=> {
    applyFilters(allRows, c3paoFilter, implFilter)
  }, [c3paoFilter, implFilter, allRows])

  const handleC3paoFilter = (filter: string) => {
    setC3paoFilter(c3paoFilter === filter ? '' : filter)
  }

  const handleImplFilter = (filter: string) => {
    setImplFilter(implFilter === filter ? '' : filter)
  }

  const totalControls = dashboard?.total ?? allRows.length

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">CMMC Level_2 System Security Plan</h1>
        <a className="underline" onClick={()=>setSel(null)} href="#">Controls</a>
      </header>
      {sel ? <Detail control={sel} onBack={async()=>{ setSel(null); await fetchRows(); await fetchDashboard() }} /> : (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-[1fr_auto] gap-3">
            <input value={q} onChange={e=>setQ(e.target.value)} placeholder="Search controls" className="border rounded-xl px-3 py-2"/>
            <select value={domain} onChange={e=>setDomain(e.target.value)} className="border rounded-xl px-3 py-2">
              <option value="">All domains</option>
              {['Access Control (AC)','Awareness & Training (AT)','Audit & Accountability (AU)','Configuration Management (CM)','Identification & Authentication (IA)','Incident Response (IR)','Maintenance (MA)','Media Protection (MP)','Personnel Security (PS)','Physical Protection (PE)','Risk Assessment (RA)','Security Assessment (CA)','System & Communications Protection (SC)','System & Information Integrity (SI)'].map(d=> <option key={d} value={d}>{d}</option>)}
            </select>
          </div>

          {dashboard && (
            <div className="space-y-4">
              {/* C3PAO Assessment Findings Filters */}
              <div className="bg-white rounded-xl p-4 border shadow-sm">
                <h3 className="font-semibold mb-3 text-gray-800">C3PAO Assessment Findings</h3>
                <div className="flex flex-wrap gap-2">
                    {C3PAO_FILTERS.map(option => (
                      <button
                        key={option.value}
                        onClick={() => handleC3paoFilter(option.value)}
                        className={`px-3 py-2 text-sm rounded-lg border transition-colors ${c3paoFilter === option.value ? option.activeClass : FILTER_INACTIVE}`}
                    >
                      {option.label} ({dashboard.c3pao?.[option.value] ?? 0} / {dashboard.total})
                    </button>
                  ))}
                </div>
              </div>

              {/* Self-Reported Implementation Status Filters */}
              <div className="bg-white rounded-xl p-4 border shadow-sm">
                <h3 className="font-semibold mb-3 text-gray-800">Self-Reported Implementation Status</h3>
                <div className="flex flex-wrap gap-2">
                    {SELF_IMPL_FILTERS.map(option => (
                      <button
                        key={option.value}
                        onClick={() => handleImplFilter(option.value)}
                        className={`px-3 py-2 text-sm rounded-lg border transition-colors ${implFilter === option.value ? option.activeClass : FILTER_INACTIVE}`}
                    >
                      {option.label} ({dashboard.impl?.[option.value] ?? 0} / {dashboard.total})
                    </button>
                  ))}
                </div>
              </div>

              {/* Active Filters Display */}
              {(c3paoFilter || implFilter) && (
                <div className="bg-blue-50 rounded-xl p-3 border border-blue-200">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-sm font-medium text-blue-800">Active filters:</span>
                    {c3paoFilter && (
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                        C3PAO: {labelForFilter(c3paoFilter, C3PAO_FILTERS)}
                        <button 
                          onClick={() => setC3paoFilter('')} 
                          className="ml-1 text-blue-600 hover:text-blue-800"
                        >
                          ×
                        </button>
                      </span>
                    )}
                    {implFilter && (
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                        Implementation: {labelForFilter(implFilter, SELF_IMPL_FILTERS)}
                        <button 
                          onClick={() => setImplFilter('')} 
                          className="ml-1 text-blue-600 hover:text-blue-800"
                        >
                          ×
                        </button>
                      </span>
                    )}
                    <button 
                      onClick={() => {setC3paoFilter(''); setImplFilter('')}} 
                      className="text-xs text-blue-600 hover:text-blue-800 underline"
                    >
                      Clear all
                    </button>
                  </div>
                  <div className="text-sm text-blue-700 mt-1">
                    Showing {rows.length} of {totalControls} requirements
                  </div>
                </div>
              )}
            </div>
          )}

          <div className="w-full overflow-auto rounded-2xl shadow">
            <table className="min-w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="p-3 text-left">Req ID</th>
                  <th className="p-3 text-left">Domain</th>
                  <th className="p-3 text-left">Title</th>
                  <th className="p-3 text-left w-56">C3PAO Assessment Findings</th>
                  <th className="p-3 text-left w-72">Self-Reported Implementation Status</th>
                </tr>
              </thead>
              <tbody>
                {rows.map(r => (
                  <tr key={r.id} className={`border-b hover:bg-gray-50 ${rowBg(r.c3pao_finding)}`}>
                    <td className="p-3 font-mono cursor-pointer" onClick={()=>setSel(r)}>{r.requirement_id}</td>
                    <td className="p-3 cursor-pointer" onClick={()=>setSel(r)}>{r.domain}</td>
                    <td className="p-3 cursor-pointer" onClick={()=>setSel(r)}>{r.title}</td>
                    <td className="p-3">
                      <select className="border rounded-xl px-2 py-1 w-full" value={r.c3pao_finding||''} onChange={async(e)=>{
                        await patchControl(r.id, { c3pao_finding: e.target.value || null }); 
                        await fetchRows(); 
                        await fetchDashboard()
                      }}>
                        <option value="">Select...</option>
                        <option value="MET">MET</option>
                        <option value="NOT_MET">NOT MET</option>
                        <option value="NA">N/A</option>
                        <option value="UNASSIGNED">UNASSIGNED</option>
                      </select>
                    </td>
                    <td className="p-3">
                      <select className="border rounded-xl px-2 py-1 w-full" value={r.self_impl_status||''} onChange={async(e)=>{
                        await patchControl(r.id, { self_impl_status: e.target.value || null }); 
                        await fetchRows(); 
                        await fetchDashboard()
                      }}>
                        <option value="">Select...</option>
                        <option>Implemented</option>
                        <option>Partially Implemented</option>
                        <option>Planned or Not Implemented</option>
                        <option>Alternative Implementation</option>
                        <option>N/A</option>
                        <option value="UNASSIGNED">UNASSIGNED</option>
                      </select>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

function Detail({ control, onBack }: { control: Control, onBack: ()=>void }){
  const [c, setC] = useState<Control>(control)
  const [provider, setProvider] = useState('')
  const [solution, setSolution] = useState('')
  const [providerLog, setProviderLog] = useState<Array<any>>([])
  const [solutionLog, setSolutionLog] = useState<Array<any>>([])
  const [evidence, setEvidence] = useState<Array<any>>([])

  useEffect(()=>{ (async()=>{
    const fresh = await getControl(c.id); setC(fresh)
    setProvider(''); setSolution('')
    setProviderLog(await listTextLog(c.requirement_id, 'provider'))
    setSolutionLog(await listTextLog(c.requirement_id, 'solution'))
    setEvidence(await listEvidence(c.requirement_id))
  })() }, [c.id])

  const saveProvider = async()=>{
    if (!provider.trim()) return
    await addTextLog(c.requirement_id, 'provider', provider.trim())
    setProvider('')
    setProviderLog(await listTextLog(c.requirement_id, 'provider'))
  }
  const saveSolution = async()=>{
    if (!solution.trim()) return
    await addTextLog(c.requirement_id, 'solution', solution.trim())
    setSolution('')
    setSolutionLog(await listTextLog(c.requirement_id, 'solution'))
  }
  const onUploadEvidence = async(files: FileList|null)=>{
    if (!files || files.length===0) return
    await uploadEvidence(c.requirement_id, files)
    setEvidence(await listEvidence(c.requirement_id))
  }

  return (
    <div className="p-6 space-y-6">
      <button onClick={onBack} className="text-sm underline">← Back</button>
      <h1 className="text-2xl font-bold">{c.requirement_id} – {c.title}</h1>
      <p className="text-gray-700 whitespace-pre-wrap">{c.statement}</p>

      {c.discussion && (<div><h2 className="font-semibold mt-2">Discussion</h2><p className="whitespace-pre-wrap">{c.discussion}</p></div>)}
      {c.further_discussion && (<div><h2 className="font-semibold mt-2">Further discussion</h2><p className="whitespace-pre-wrap">{c.further_discussion}</p></div>)}
      {c.assessment_objectives && c.assessment_objectives.trim() && (<div><h2 className="font-semibold mt-2">Assessment Objectives</h2><p className="whitespace-pre-wrap text-sm">{c.assessment_objectives}</p></div>)}
      {c.assessment_methods && c.assessment_methods.trim() && (<div><h2 className="font-semibold mt-2">Potential Assessment Methods and Objectives</h2><p className="whitespace-pre-wrap text-sm">{c.assessment_methods}</p></div>)}
      {c.key_references && (<div><h2 className="font-semibold mt-2">Key references</h2><p className="whitespace-pre-wrap">{c.key_references}</p></div>)}

      <section className="rounded-2xl border p-4 bg-white/50 space-y-3">
        <h2 className="font-semibold">Control Provider</h2>
        <div className="flex gap-2 items-start">
          <input className="flex-1 border rounded-xl px-3 py-2" value={provider} onChange={e=>setProvider(e.target.value)} placeholder="e.g., Internal IT, MSP, Cloud provider" />
          <button className="px-3 py-2 rounded-xl border shadow-sm" onClick={saveProvider}>Save</button>
        </div>
        {providerLog.length>0 && (
          <div className="mt-2 space-y-2">
            {providerLog.map((entry) => (
              <div key={entry.id} className="flex items-start gap-2 p-2 rounded-lg border bg-white">
                <div className="text-xs text-gray-500 w-44 shrink-0">{new Date(entry.ts).toISOString()}</div>
                <div className="whitespace-pre-wrap flex-1 text-sm">{entry.text}</div>
                <button className="text-xs px-2 py-1 rounded border" onClick={async()=>{ await deleteTextLog(entry.id); setProviderLog(await listTextLog(c.requirement_id,'provider')) }}>Delete</button>
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="rounded-2xl border p-4 bg-white/50 space-y-3">
        <h2 className="font-semibold">What is the Solution, and how is it implemented?</h2>
        <div className="flex gap-2 items-start">
          <textarea className="flex-1 border rounded-xl px-3 py-2 min-h-[120px]" value={solution} onChange={e=>setSolution(e.target.value)} placeholder="Describe the solution and implementation details" />
          <button className="px-3 py-2 rounded-xl border shadow-sm" onClick={saveSolution}>Save</button>
        </div>
        {solutionLog.length>0 && (
          <div className="mt-2 space-y-2">
            {solutionLog.map((entry) => (
              <div key={entry.id} className="flex items-start gap-2 p-2 rounded-lg border bg-white">
                <div className="text-xs text-gray-500 w-44 shrink-0">{new Date(entry.ts).toISOString()}</div>
                <div className="whitespace-pre-wrap flex-1 text-sm">{entry.text}</div>
                <button className="text-xs px-2 py-1 rounded border" onClick={async()=>{ await deleteTextLog(entry.id); setSolutionLog(await listTextLog(c.requirement_id,'solution')) }}>Delete</button>
              </div>
            ))}
          </div>
        )}
      </section>

      <div className="mt-6 space-y-3">
        <h2 className="font-semibold mb-2">Evidence</h2>
        <input type="file" multiple className="border rounded-xl p-2" onChange={e=>onUploadEvidence(e.target.files)} />
        {evidence.length>0 && (
          <div className="space-y-2">
            {evidence.map(ev => (
              <div key={ev.id} className="flex items-center justify-between p-2 rounded-lg border bg-white text-sm">
                <div className="flex items-center gap-3 overflow-hidden">
                  <span className="text-xs text-gray-500 shrink-0 w-44">{new Date(ev.ts).toISOString()}</span>
                  <span className="truncate max-w-[26rem]" title={`${ev.filename} (${ev.size} bytes)`}>{ev.filename}</span>
                  <span className="text-xs text-gray-500 shrink-0">{ev.size} bytes</span>
                </div>
                <button className="text-xs px-2 py-1 rounded border" onClick={async()=>{ await deleteEvidence(ev.id); setEvidence(await listEvidence(c.requirement_id)) }}>Delete</button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
