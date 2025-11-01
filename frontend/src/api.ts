import axios from 'axios'

const api = axios.create({ baseURL: import.meta.env.VITE_API_BASE || 'http://localhost:8000' })

export type Control = {
  id: number
  requirement_id: string
  domain: string
  title: string
  statement: string
  discussion?: string
  further_discussion?: string
  key_references?: string
  assessment_objectives?: string
  assessment_methods?: string
  c3pao_finding?: 'MET'|'NOT_MET'|'NA'|'UNASSIGNED'|null
  self_impl_status?: 'Implemented'|'Partially Implemented'|'Planned or Not Implemented'|'Alternative Implementation'|'N/A'|'UNASSIGNED'|null
}

export async function listControls(q = '', domain = '') {
  const { data } = await api.get<Control[]>('/controls', { params: { q, domain } })
  return data
}
export async function getControl(id: number) {
  const { data } = await api.get<Control>(`/controls/${id}`)
  return data
}
export async function patchControl(id: number, body: Partial<Control>) {
  const { data } = await api.patch<Control>(`/controls/${id}`, body)
  return data
}
export async function listTextLog(requirement_id: string, kind?: string) {
  const { data } = await api.get(`/controls/${requirement_id}/textlog`, { params: { kind } })
  return data as Array<{id:number, requirement_id:string, kind:string, text:string, ts:string}>
}
export async function addTextLog(requirement_id: string, kind: 'provider'|'solution', text: string) {
  const { data } = await api.post(`/controls/${requirement_id}/textlog`, { kind, text })
  return data
}
export async function deleteTextLog(id: number) {
  await api.delete(`/textlog/${id}`)
}
export async function listEvidence(requirement_id: string) {
  const { data } = await api.get(`/controls/${requirement_id}/evidence`)
  return data as Array<{id:number, requirement_id:string, filename:string, size:number, ts:string}>
}
export async function uploadEvidence(requirement_id: string, files: FileList) {
  const fd = new FormData()
  Array.from(files).forEach(f => fd.append('files', f))
  const { data } = await api.post(`/controls/${requirement_id}/evidence`, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
  return data
}
export async function deleteEvidence(id: number) {
  await api.delete(`/evidence/${id}`)
}

export async function getDashboard() {
  const { data } = await api.get('/dashboard')
  return data as {
    total: number
    c3pao: Record<string, number>
    impl: Record<string, number>
  }
}
