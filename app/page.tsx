'use client';
import { useEffect, useRef, useState } from 'react';
import { BookOpen, Check, ChevronRight, Code2, FileCode2, FolderOpen, Play, Plus, Save, ShieldCheck, Terminal, X, LoaderCircle, WandSparkles, Eye } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { NativeSelect, NativeSelectOption } from '@/components/ui/native-select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import Session from './session';

type PracticeModule = { id: string; name: string; enabled: boolean; command: string };
type Doc = { title: string; url: string };
type Run = { passed: boolean; output: string; tests: { name: string; action: string }[]; elapsed: number; stale?: boolean; fingerprint: string };
type Project = { module?: PracticeModule; id: string; track: string; runner: string; entry: string; generated?: boolean; title: string; level: string; summary: string; skills: string[]; requirements: string[]; docs: Doc[]; run?: Run };
type FileEntry = { path: string; editable: boolean };
type FileData = { content: string; revision: string; editable: boolean };
type Feedback = { feedback: string; observations: string[]; questions: string[]; documentation: Doc[] };

const TRACKS: Record<string, string> = { go: 'Go', rust: 'Rust', javascript: 'Modern JavaScript', react: 'React', vue: 'Vue', html: 'HTML', 'html-css': 'HTML + CSS', tailwind: 'Tailwind', ruby: 'Ruby', rails: 'Ruby on Rails' };
type Generation = { id: string; status: string; message: string; projectId?: string; title?: string };

async function api<T = Record<string, never>>(path: string, body?: object, method = 'POST'): Promise<T> {
  const res = await fetch('/api' + path, body ? { method, headers: { 'Content-Type': 'application/json', 'X-Code-Gym': '1' }, body: JSON.stringify(body) } : { cache: 'no-store' });
  const data = await res.json() as T & { error?: string };
  if (!res.ok) throw new Error(data.error || 'Request failed');
  return data;
}

function Editor({ value, readOnly, onChange, identity }: { value: string; readOnly: boolean; onChange: (s: string) => void; identity: string }) {
  const host = useRef<HTMLDivElement>(null);
  const callback = useRef(onChange); callback.current = onChange;
  const latestValue = useRef(value); latestValue.current = value;
  const readOnlyRef = useRef(readOnly); readOnlyRef.current = readOnly;
  const viewRef = useRef<import('codemirror').EditorView | null>(null);
  const configure = useRef<((value: boolean) => void) | null>(null);
  const [ready, setReady] = useState(false);
  useEffect(() => {
    let gone = false; let destroy: (() => void) | undefined;
    setReady(false);
    Promise.all([import('codemirror'), import('@codemirror/theme-one-dark'), import('@codemirror/state'), languageFor(identity)]).then(([cm, theme, state, language]) => {
      if (gone || !host.current) return;
      const mode = new state.Compartment();
      const modeExtensions = (locked: boolean) => [state.EditorState.readOnly.of(locked), cm.EditorView.editable.of(!locked), cm.EditorView.contentAttributes.of({ 'aria-label': identity, 'aria-readonly': String(locked) })];
      const view = new cm.EditorView({ parent: host.current, doc: latestValue.current, extensions: [cm.basicSetup, ...language, theme.oneDark, mode.of(modeExtensions(readOnlyRef.current)), cm.EditorView.updateListener.of(u => { if (u.docChanged) callback.current(u.state.doc.toString()); }), cm.EditorView.theme({ '&': { height: '100%', backgroundColor: '#10151c', fontSize: '15px' }, '.cm-scroller': { overflow: 'auto', fontFamily: '"SFMono-Regular", Consolas, monospace', lineHeight: '1.7' }, '.cm-gutters': { backgroundColor: '#10151c', color: '#657385', border: 'none' }, '.cm-content': { padding: '20px 0' } })] });
      viewRef.current = view; configure.current = locked => view.dispatch({ effects: mode.reconfigure(modeExtensions(locked)) });
      destroy = () => { configure.current = null; viewRef.current = null; view.destroy(); }; setReady(true);
    }).catch(() => { /* Accessible plain-text fallback remains available. */ });
    return () => { gone = true; destroy?.(); };
  }, [identity]);
  useEffect(() => { configure.current?.(readOnly); }, [readOnly]);
  return <div className="editor-host"><div ref={host} className="cm-host" />{!ready && <textarea aria-label={identity} value={value} readOnly={readOnly} onChange={e => onChange(e.target.value)} className="fallback-editor" spellCheck={false} />}</div>;
}

async function languageFor(path: string) {
  if (path.endsWith('.go')) return [(await import('@codemirror/lang-go')).go()];
  if (path.endsWith('.rb')) { const [{StreamLanguage},{ruby}] = await Promise.all([import('@codemirror/language'),import('@codemirror/legacy-modes/mode/ruby')]); return [StreamLanguage.define(ruby)]; }
  if (path.endsWith('.rs')) return [(await import('@codemirror/lang-rust')).rust()];
  if (path.endsWith('.vue')) return [(await import('@codemirror/lang-vue')).vue()];
  if (/\.[jt]sx?$/.test(path)) return [(await import('@codemirror/lang-javascript')).javascript({ jsx: true, typescript: /\.tsx?$/.test(path) })];
  if (path.endsWith('.html')) return [(await import('@codemirror/lang-html')).html()];
  if (path.endsWith('.css')) return [(await import('@codemirror/lang-css')).css()];
  if (path.endsWith('.json')) return [(await import('@codemirror/lang-json')).json()];
  return [];
}

export default function Home() {
  const [route, setRoute] = useState<{mode: string; project: string} | null>(null);
  useEffect(() => { const q = new URLSearchParams(window.location.search); setRoute({mode:q.get('mode') || '',project:q.get('project') || ''}); }, []);
  if (!route) return <main className="session-loading"><Code2/><p>Opening your gym…</p></main>;
  return route.mode === 'session' ? <Session projectId={route.project}/> : <Dashboard/>;
}

function Dashboard() {
  const [track, setTrack] = useState('go');
  const [generatorOpen, setGeneratorOpen] = useState(false);
  const [idea, setIdea] = useState('');
  const [generationTrack, setGenerationTrack] = useState('go');
  const [timebox, setTimebox] = useState('A weekend');
  const [generation, setGeneration] = useState<Generation | null>(null);
  const [generationError, setGenerationError] = useState('');
  const [preview, setPreview] = useState('');
  const [projects, setProjects] = useState<Project[]>([]);
  const [selected, setSelected] = useState('');
  const [files, setFiles] = useState<FileEntry[]>([]);
  const [path, setPath] = useState('main.go');
  const [file, setFile] = useState<FileData | null>(null);
  const [draft, setDraft] = useState('');
  const [busy, setBusy] = useState('');
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [run, setRun] = useState<Run | null>(null);
  const [feedback, setFeedback] = useState<Feedback | null>(null);
  const [question, setQuestion] = useState('');
  const [panel, setPanel] = useState('brief');
  const [newFile, setNewFile] = useState<string | null>(null);
  const [reload, setReload] = useState(0);
  const project = projects.find(p => p.id === selected);
  const dirty = !!file && file.editable && draft !== file.content;
  const visibleProjects = projects.filter(p => p.track === track);
  const completed = visibleProjects.filter(p => p.run?.passed && !p.run.stale).length;
  const generating = generation?.status === 'queued' || generation?.status === 'running';
  const loading = !file;
  const runStale = !!run && (run.stale || dirty);

  async function refreshProjects() { const data = await api<{ projects: Project[] }>('/projects'); setProjects(data.projects); return data.projects as Project[]; }
  useEffect(() => { refreshProjects().then(ps => { const first = ps.find(p => p.module?.enabled !== false) ?? ps[0]; if (first) { setSelected(first.id); setTrack(first.track); setGenerationTrack(first.track); setPath(first.entry); setRun(first.run ?? null); } }).catch(e => setError(e.message)); const pending = localStorage.getItem('omagym-generation'); if (pending) api<Generation>(`/generation?id=${pending}`).then(setGeneration).catch(() => localStorage.removeItem('omagym-generation')); }, []);
  useEffect(() => {
    if (!selected) return;
    let cancelled = false;
    setFile(null); setError('');
    Promise.all([api<{ files: FileEntry[] }>(`/files?project=${selected}`), api<FileData>(`/file?project=${selected}&path=${encodeURIComponent(path)}`)]).then(([listing, data]) => {
      if (!cancelled) { setFiles(listing.files); setFile(data); setDraft(data.content); }
    }).catch(e => { if (!cancelled) setError(e.message); });
    return () => { cancelled = true; };
  }, [selected, path, reload]);
  useEffect(() => { const refresh = () => { void refreshProjects().catch(e => setError(e.message)); }; window.addEventListener('focus', refresh); return () => window.removeEventListener('focus', refresh); }, []);
  useEffect(() => { const handler = (e: BeforeUnloadEvent) => { if (dirty) e.preventDefault(); }; window.addEventListener('beforeunload', handler); return () => window.removeEventListener('beforeunload', handler); }, [dirty]);

  const reviewState = useRef({ project, path, draft, dirty, run });
  reviewState.current = { project, path, draft, dirty, run };
  useEffect(() => {
    const context = (document as Document & { modelContext?: { registerTool: (tool: object, options: { signal: AbortSignal }) => void | Promise<void> } }).modelContext;
    if (!context?.registerTool) return;
    const lifecycle = new AbortController();
    try {
      void Promise.resolve(context.registerTool({
        name: 'inspect_omagym_practice', title: 'Inspect current exercise',
        description: 'Read the selected exercise brief, visible file draft and latest test result for feedback-only review. Does not change files or give solutions.',
        inputSchema: { type: 'object', properties: {}, additionalProperties: false },
        annotations: { readOnlyHint: true, untrustedContentHint: true },
        execute(input: unknown) {
          if (!input || typeof input !== 'object' || Array.isArray(input) || Object.keys(input).length) throw new Error('Expected an empty object.');
          return reviewState.current;
        },
      }, { signal: lifecycle.signal })).catch(() => {});
    } catch { /* Optional browser capability. */ }
    return () => lifecycle.abort();
  }, []);

  async function save() {
    if (!dirty || !file) return;
    const data = await api<FileData>('/file', { project: selected, path, content: draft, revision: file.revision });
    setFile(data); setNotice('Saved to project folder');
    if (run) setRun({ ...run, stale: true });
    setProjects(ps => ps.map(p => p.id === selected && p.run ? { ...p, run: { ...p.run, stale: true } } : p));
  }
  async function task(label: string, work: () => Promise<void>) {
    setBusy(label); setError(''); setNotice('');
    try { await work(); } catch (e) { setError(e instanceof Error ? e.message : 'Something went wrong'); } finally { setBusy(''); }
  }
  async function chooseProject(id: string) {
    await task('Opening project', async () => { await save(); setSelected(id); const next = projects.find(p => p.id === id); setTrack(next?.track ?? track); setPath(next?.entry ?? 'main.go'); setPreview(''); setRun(projects.find(p => p.id === id)?.run ?? null); setFeedback(null); setQuestion(''); setPanel('brief'); });
  }
  async function chooseTrack(next: string) {
    const first = projects.find(p => p.track === next);
    if (first) await chooseProject(first.id); else setTrack(next);
  }
  async function generate() {
    setGenerationError('');
    try {
      await save();
      const job = await api<Generation>('/generate', { prompt: idea, track: generationTrack, timebox });
      setGeneration(job); localStorage.setItem('omagym-generation', job.id);
    } catch(e) { setGenerationError(e instanceof Error ? e.message : 'Could not start generation'); }
  }
  useEffect(() => {
    if (!generation || !generating) return;
    let cancelled = false;
    const timer = setInterval(async () => {
      try {
        const job = await api<Generation>(`/generation?id=${generation.id}`);
        if (cancelled) return;
        setGeneration(job);
        if (job.status === 'complete') { await refreshProjects(); localStorage.removeItem('omagym-generation'); }
        if (job.status === 'failed') localStorage.removeItem('omagym-generation');
      } catch(e) { if (!cancelled) setGenerationError(e instanceof Error ? e.message : 'Waiting for the generator'); }
    }, 2000);
    return () => { cancelled = true; clearInterval(timer); };
  }, [generation?.id, generating]);
  async function openGenerated() {
    if (!generation?.projectId) return;
    await task('Opening project', async () => {
      const updated = await refreshProjects(); const next = updated.find(p => p.id === generation.projectId);
      if (next) { await save(); setSelected(next.id); setTrack(next.track); setPath(next.entry); setRun(null); setFeedback(null); setPanel('brief'); setGeneratorOpen(false); setPreview(''); }
    });
  }
  async function buildPreview() { await task('Building preview', async () => { await save(); const result = await api<{path: string}>('/preview', {project: selected}); setPreview(`http://${window.location.hostname}:4312${result.path}?v=${Date.now()}`); setPanel('preview'); }); }
  async function chooseFile(name: string) { if (name === path) return; await task('Opening file', async () => { await save(); setPath(name); }); }
  async function test() {
    await task('Running tests', async () => {
      await save(); setPanel('tests');
      const data = await api<Run>('/run', { project: selected });
      setRun(data); await refreshProjects();
    });
  }
  async function coach() {
    await task('Coach is reading', async () => { await save(); setPanel('coach'); const data = await api<Feedback>('/coach', { project: selected, question }); setFeedback(data); });
  }
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if ((e.metaKey || e.ctrlKey) && e.key === 's') { e.preventDefault(); if (!busy && file) void task('Saving', save); } };
    window.addEventListener('keydown', handler); return () => window.removeEventListener('keydown', handler);
  });

  return <main className="gym-shell">
    <header className="topbar"><div className="brand"><span className="brand-icon"><Code2 size={23}/></span> oma<span>gym</span><span className="edition">MAKE A WEEKEND OF IT</span></div><Button className="new-project-button" variant="outline" onClick={() => {setGenerationTrack(track);setGeneratorOpen(true);}}><WandSparkles/> {generating ? 'Designing your project…' : generation?.status==='complete' ? 'Your project is ready' : 'Create a project'}</Button><div className="top-meta"><span className="online-dot"/> Local workspace <span className="separator">/</span> <ShieldCheck size={15}/> Feedback-only coach</div></header>
    <div className="workspace">
      <aside className="project-rail">
        <div className="rail-heading"><span className="eyebrow">TRAINING PATH</span><span className="go-mark">{TRACKS[track]}</span></div>
        <h1>Learn by shipping.</h1><p className="muted rail-intro">{visibleProjects.length} projects in this track.<br/>Every line is yours.</p><NativeSelect aria-label="Language or framework" value={track} disabled={!!busy || loading || !projects.length} onChange={e => chooseTrack(e.target.value)}>{Object.entries(TRACKS).map(([key,label]) => <NativeSelectOption key={key} value={key}>{label} · {projects.filter(p=>p.track===key).length}{projects.find(p=>p.track===key)?.module?.enabled === false ? ' · module off' : ''}</NativeSelectOption>)}</NativeSelect>
        <nav aria-label="Exercises">{visibleProjects.map((p,i) => <button key={p.id} className={'project-link ' + (selected === p.id ? 'selected' : '')} disabled={!!busy || loading} onClick={() => chooseProject(p.id)}><span className={'project-number '+(p.run?.passed && !p.run.stale ? 'done':'')}>{p.run?.passed && !p.run.stale ? <Check size={16}/> : String(i+1).padStart(2,'0')}</span><span><strong>{p.title}</strong><small>{p.generated ? 'Your project' : p.level.split(' · ').at(-1)}</small></span>{selected === p.id && <ChevronRight size={15}/>}</button>)}</nav>
        <div className="progress-block"><div><span>YOUR PROGRESS</span><strong>{completed} / {visibleProjects.length}</strong></div><Progress value={visibleProjects.length ? completed/visibleProjects.length*100 : 0}/><p>Passing tests complete a project.</p></div>
        <div className="rail-note"><ShieldCheck size={20}/><p>The coach can read your code.<br/>Only you can write it.</p></div>
      </aside>
      <section className="work-area">
        <div className="workspace-heading"><div><div className="eyebrow">{TRACKS[project?.track || track]} WORKSPACE <ChevronRight size={12}/> {project?.level || 'Foundations'}</div><h2>{project?.title || 'Word counter'}</h2></div><div className="actions">{project?.runner === 'browser' && <Button variant="outline" disabled={!!busy || loading || project?.module?.enabled === false} onClick={buildPreview}><Eye/> Preview</Button>}<Button variant="outline" disabled={!!busy || !dirty} onClick={() => task('Saving', save)}><Save/> Save</Button><Button className="run-button" disabled={!!busy || loading || project?.module?.enabled === false} onClick={test}>{busy === 'Running tests' ? <LoaderCircle className="spin"/> : <Play/>} {busy === 'Running tests' ? 'Running…' : 'Run tests'}</Button></div></div>
        {(error || notice || busy) && <div className={'message '+(error ? 'error':'')} role={error ? 'alert':'status'}>{error || busy || notice}{!busy && <button aria-label="Dismiss message" onClick={() => {setError('');setNotice('');}}><X size={14}/></button>}</div>}
        {project?.module && !project.module.enabled && <div className="module-notice">Enable the {project.module.name} module in your terminal: <code>{project.module.command}</code><span>Your files stay available while this module is disabled.</span></div>}
        <div className="coding-grid">
          <section className="editor-panel">
            <div className="file-layout"><aside className="file-tree"><div className="file-heading"><FolderOpen size={15}/><span>FILES</span><button title="New file" aria-label="New file" disabled={!!busy || loading} onClick={() => setNewFile('')}><Plus size={16}/></button></div>{newFile !== null && <form onSubmit={e => {e.preventDefault(); void task('Creating file', async () => {await save(); await api('/file', {project:selected,path:newFile,content:'',create:true});setPath(newFile);setNewFile(null);setReload(x=>x+1);});}}><input aria-label="New file path" autoFocus placeholder="helpers.go" value={newFile} onChange={e=>setNewFile(e.target.value)}/><Button type="submit" disabled={!!busy || !newFile}>Create</Button><button type="button" aria-label="Cancel new file" onClick={()=>setNewFile(null)}><X size={14}/></button></form>}{files.map(f => <button key={f.path} title={f.path} disabled={!!busy || loading} className={'file-link '+(path===f.path?'active':'')} onClick={() => chooseFile(f.path)}><FileCode2 size={14}/><span>{f.path}</span>{!f.editable && <span className="readonly-dot" title="Read only">·</span>}</button>)}</aside>
              <div className="editor-column"><div className="editor-tab"><FileCode2 size={15}/>{path}{dirty && <span className="dirty-dot"/>}<span className="file-mode">{file?.editable ? 'EDITABLE' : 'READ ONLY'}</span></div>{file && <Editor key={`${selected}/${path}/${reload}`} identity={`${selected}/${path}`} value={draft} readOnly={!file.editable || !!busy} onChange={s => { setDraft(s); setFeedback(null); }}/>}<div className="editor-status"><span>{path.split('.').at(-1)?.toUpperCase() || 'Text'}</span><span>UTF-8 <span className="separator">/</span> {dirty ? 'Unsaved changes' : 'Saved on disk'}</span></div></div>
            </div>
          </section>
          <aside className="learning-panel"><Tabs value={panel} onValueChange={v => setPanel(String(v))}><TabsList variant="line" className="panel-tabs"><TabsTrigger value="brief"><BookOpen/> Brief</TabsTrigger><TabsTrigger value="tests"><Terminal/> Tests</TabsTrigger><TabsTrigger value="coach"><ShieldCheck/> Coach</TabsTrigger>{project?.runner === 'browser' && <TabsTrigger value="preview"><Eye/> Preview</TabsTrigger>}</TabsList>
            <TabsContent value="brief"><div className="panel-content"><span className="eyebrow">THE CHALLENGE</span><h3>{project?.title || 'Your next project'}</h3><p>{project?.summary || 'Connecting to your local gym…'}</p><div className="skill-tags">{project?.skills.map(s => <span key={s}>{s}</span>)}</div><h4>What you’re building</h4><ol className="requirements">{project?.requirements.map((r,i) => <li key={r}><span>{String(i+1).padStart(2,'0')}</span><p>{r}</p></li>)}</ol><h4>Read the docs</h4><DocLinks docs={project?.docs || []}/></div></TabsContent>
            <TabsContent value="tests"><div className="panel-content"><span className="eyebrow">TEST BENCH</span><h3>{busy === 'Running tests' ? 'Running your suite…' : run ? runStale ? 'Code changed' : run.passed ? 'All checks passed' : 'Keep going.' : 'Make it work.'}</h3><p>{runStale ? 'These results are from an older version. Run tests again to check your current code.' : 'Run the suite to see which parts of the contract your code meets.'}</p>{run && <><div className="test-summary">{run.tests.filter(t=>t.action==='pass').length} passed <span>/</span> {run.tests.filter(t=>t.action==='fail').length} failed <span>/</span> {run.elapsed.toFixed(1)}s</div><div className="test-list">{run.tests.map(t => <div key={t.name} className={t.action}><span>{t.action==='pass'?'✓':t.action==='fail'?'×':'−'}</span>{t.name}</div>)}</div><details open={!run.passed}><summary>Full test output</summary><pre className="terminal-output">{run.output || 'No test output.'}</pre></details></>}{!run && <div className="empty-state"><Terminal size={30}/><p>Your first run is a starting point.<br/>Failing tests are part of the workout.</p></div>}</div></TabsContent>
            <TabsContent value="coach"><div className="panel-content"><span className="eyebrow">REFLECT, THEN TRY AGAIN</span><h3>A second pair of eyes.</h3><p>Feedback on your code and tests. Questions to think through. Documentation to explore.</p><label className="question-label" htmlFor="coach-question">What would you like reviewed? <span>(optional)</span></label><textarea id="coach-question" className="coach-question" maxLength={2000} value={question} onChange={e=>setQuestion(e.target.value)} placeholder="Am I handling errors consistently?" disabled={!!busy}/><Button className="coach-button" variant="outline" disabled={!!busy || loading} onClick={coach}>{busy==='Coach is reading'?<LoaderCircle className="spin"/>:<ShieldCheck/>}{busy==='Coach is reading'?'Reading your project…':'Ask for feedback'}</Button><p className="coach-context">Reads saved project files and the latest test run through your installed Codex. No solutions or code edits.</p>{feedback && <div className="feedback"><p>{feedback.feedback}</p>{feedback.observations.length>0 && <><h4>Observations</h4><ul>{feedback.observations.map(s=><li key={s}>{s}</li>)}</ul></>}{feedback.questions.length>0 && <><h4>Think about</h4><ul>{feedback.questions.map(s=><li key={s}>{s}</li>)}</ul></>}<h4>Explore the docs</h4><DocLinks docs={feedback.documentation}/></div>}</div></TabsContent>
            {project?.runner === 'browser' && <TabsContent value="preview"><div className="preview-panel"><div className="preview-toolbar"><span>Saved source preview</span><Button variant="outline" disabled={!!busy} onClick={buildPreview}>Refresh preview</Button></div>{preview ? <iframe key={preview} title="Exercise preview" src={preview} sandbox="allow-scripts allow-same-origin allow-forms"/> : <div className="empty-state"><Eye/><p>Build your current source to see it here.</p><Button variant="outline" disabled={!!busy} onClick={buildPreview}>Build preview</Button></div>}</div></TabsContent>}
          </Tabs></aside>
        </div>
      </section>
    </div>
    <Dialog open={generatorOpen} onOpenChange={setGeneratorOpen}><DialogContent className="generator-dialog"><DialogHeader><DialogTitle>What are you building this weekend?</DialogTitle><DialogDescription>Turn an idea into a complete brief, starter files, a checked test suite, and your feedback-only coach.</DialogDescription></DialogHeader>
      <label htmlFor="project-idea">Your project idea</label><textarea id="project-idea" className="coach-question idea-input" value={idea} onChange={e=>setIdea(e.target.value)} maxLength={4000} placeholder="A reading tracker with a searchable bookshelf, reading goals, and progress. I want to practice React state and forms." disabled={generating}/>
      <div className="generator-options"><label>Language / framework<NativeSelect aria-label="Project language" value={generationTrack} onChange={e=>setGenerationTrack(e.target.value)} disabled={generating}>{Object.entries(TRACKS).map(([key,label])=><NativeSelectOption key={key} value={key}>{label}</NativeSelectOption>)}</NativeSelect></label><label>Time to spend<NativeSelect aria-label="Project timebox" value={timebox} onChange={e=>setTimebox(e.target.value)} disabled={generating}><NativeSelectOption>An afternoon</NativeSelectOption><NativeSelectOption>A weekend</NativeSelectOption><NativeSelectOption>A week of evenings</NativeSelectOption></NativeSelect></label></div>
      {generationError && <p role="alert" className="generation-error">{generationError}</p>}
      {generation && <div className={'generation-status '+generation.status} role="status">{generating && <LoaderCircle className="spin"/>}<div><strong>{generation.status==='complete' ? generation.title : generation.status==='failed' ? 'Couldn’t validate this project' : 'Building your workout'}</strong><p>{generation.message}</p>{generating && <small>You can close this panel. Generation continues here, and may take several minutes.</small>}</div></div>}
      {generation?.status==='complete' ? <div className="generator-options"><Button disabled={!!busy || loading} onClick={openGenerated}>Open your project <ChevronRight/></Button><Button variant="outline" onClick={()=>setGeneration(null)}>Design another</Button></div> : <Button disabled={generating || !!busy || idea.trim().length<20} onClick={generate}><WandSparkles/> {generating ? 'Designing and checking…' : 'Generate project'}</Button>}
      <p className="generator-footnote">The designer checks that the starter needs your work and a private reference passes the tests. Only the unsolved project is saved.</p>
    </DialogContent></Dialog>
    <footer><span><span className="online-dot"/> {TRACKS[track].toUpperCase()} TRAINING PATH</span><span>Write → Test → Reflect → Repeat</span><span>Ctrl / ⌘ S to save</span></footer>
    <p className="community-notice">Independent community project. Not officially supported or endorsed by DHH or Omacom.</p>
  </main>;
}
function DocLinks({ docs }: { docs: Doc[] }) { return <div className="doc-links">{docs.map(d=><a key={d.url} href={d.url} target="_blank" rel="noreferrer"><BookOpen size={15}/><span>{d.title}</span><span>↗</span></a>)}</div>; }
