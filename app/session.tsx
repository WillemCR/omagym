'use client';
import { useCallback, useEffect, useRef, useState } from 'react';
import { ArrowUpRight, BookOpen, Check, CheckCircle2, ChevronRight, Clipboard, Code2, Eye, FileCode2, FolderOpen, LoaderCircle, Play, RefreshCw, ShieldCheck, Terminal } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

type PracticeModule = { id: string; name: string; enabled: boolean; command: string };
type Doc = { title: string; url: string };
type Run = { passed: boolean; output: string; tests: { name: string; action: string }[]; elapsed: number; stale: boolean; fingerprint: string };
type Feedback = { feedback: string; observations: string[]; questions: string[]; documentation: Doc[]; fingerprint: string; stale: boolean; reviewedAt: number; testFingerprint: string | null };
type Status = { project: { module?: PracticeModule; id: string; title: string; track: string; level: string; summary: string; skills: string[]; requirements: string[]; docs: Doc[]; runner: string }; folder: string; files: string[]; fingerprint: string; busy: boolean; run: Run | null; feedback: Feedback | null };

async function request<T>(path: string, body?: object): Promise<T> {
  const response = await fetch('/api'+path, {signal:AbortSignal.timeout(body?240000:8000),...(body ? {method:'POST',headers:{'Content-Type':'application/json','X-Code-Gym':'1'},body:JSON.stringify(body)} : {cache:'no-store' as const})});
  const value = await response.json() as T & {error?: string};
  if (!response.ok) throw new Error(value.error || 'The request could not finish.');
  return value;
}

function Docs({docs}: {docs: Doc[]}) {
  return <div className="session-docs">{docs.map(doc => <a href={doc.url} key={doc.url} target="_blank" rel="noreferrer"><BookOpen size={16}/><span>{doc.title}</span><ArrowUpRight size={15}/></a>)}</div>;
}

export default function Session({projectId}: {projectId: string}) {
  const [status, setStatus] = useState<Status | null>(null);
  const [connectionError, setConnectionError] = useState('');
  const [actionError, setActionError] = useState('');
  const [busy, setBusy] = useState('');
  const [tab, setTab] = useState('brief');
  const [question, setQuestion] = useState('');
  const [copied, setCopied] = useState('');
  const [preview, setPreview] = useState<{url: string; fingerprint: string} | null>(null);
  const sequence = useRef(0);
  const refreshing = useRef(false);
  const live = useRef(true);
  const refresh = useCallback(async () => {
    if (refreshing.current) return;
    refreshing.current = true;
    const seq = ++sequence.current;
    try {
      const data = await request<Status>('/status?project='+encodeURIComponent(projectId));
      if (live.current && seq === sequence.current) {setStatus(data);setConnectionError('');}
    } catch(e) {if (live.current && seq === sequence.current) setConnectionError(e instanceof Error ? e.message : 'The gym is unavailable.');}
    finally {refreshing.current = false;}
  }, [projectId]);
  useEffect(() => {
    live.current = true;
    document.title = `Omagym [${projectId}] · Practice session`;
    void refresh();
    const timer = window.setInterval(() => {if (!document.hidden) void refresh();}, 2000);
    const focus = () => {if (!document.hidden) void refresh();};
    document.addEventListener('visibilitychange', focus); window.addEventListener('focus', focus);
    return () => {live.current = false; sequence.current++; clearInterval(timer);document.removeEventListener('visibilitychange', focus);window.removeEventListener('focus', focus);};
  }, [refresh, projectId]);
  useEffect(() => {if (status) document.title = `Omagym [${projectId}] · ${status.project.title}`;}, [status?.project.title, projectId]);
  useEffect(() => {if (!copied) return;const timer = setTimeout(() => setCopied(''), 2000);return () => clearTimeout(timer);}, [copied]);

  async function copy(text: string, kind: string) {
    try {await navigator.clipboard.writeText(text);setCopied(kind);} catch {setActionError('Could not copy. Select the text and copy it manually.');}
  }
  async function action(kind: string) {
    if (busy || status?.busy) return;
    setBusy(kind); setActionError('');setTab(kind === 'run' ? 'tests' : kind === 'coach' ? 'coach' : 'preview');
    try {
      if (kind === 'preview') {
        const result = await request<{path: string; fingerprint: string}>('/preview', {project:projectId});
        setPreview({url:`http://${window.location.hostname}:4312${result.path}?v=${Date.now()}`,fingerprint:result.fingerprint});
      } else await request('/'+kind, {project:projectId,...(kind==='coach'?{question}:{})});
      await refresh();
    } catch(e) {setActionError(e instanceof Error ? e.message : 'Connection lost. Check status before retrying.');}
    finally {setBusy('');void refresh();}
  }
  const disabled = !!busy || !!status?.busy || !status || !!connectionError;
  const project = status?.project;
  const run = status?.run;
  const feedback = status?.feedback;
  const passed = run?.tests.filter(t=>t.action==='pass').length || 0;

  return <main className="session-shell">
    <header className="session-top"><a className="session-brand" href="/" target="_blank" rel="noreferrer" aria-label="Open Omagym library"><Code2 size={21}/><span>oma<b>gym</b></span></a><span className="session-label">PRACTICE SESSION</span><span className={'session-connection '+(connectionError?'offline':'')}><i/>{connectionError?'Disconnected':'Local'}</span></header>
    <div className="session-main">
      <div className="session-breadcrumb"><span>{project?.track || 'YOUR WORKSPACE'}</span><ChevronRight size={12}/>{project?.level || 'Getting ready'}</div>
      <h1>{project?.title || 'Opening your workout…'}</h1>
      <p className="session-subtitle">Your tools. Your code. A little perspective.</p>
      <div className="session-folder"><FolderOpen size={16}/><code>{status?.folder || 'Connecting to your project folder'}</code><button title="Copy project folder" aria-label="Copy project folder" disabled={!status} onClick={()=>void copy(status!.folder,'folder')}>{copied==='folder'?<Check size={15}/>:<Clipboard size={15}/>}</button></div>
      {connectionError && <div className="session-alert" role="alert"><p>{connectionError}</p><Button variant="outline" onClick={()=>void refresh()}>Retry connection</Button><small>From your terminal: <code>omagym server start</code></small></div>}
      {actionError && <div className="session-alert" role="alert"><p>{actionError}</p><button onClick={()=>setActionError('')}>Dismiss</button></div>}
      {project?.module && !project.module.enabled && <div className="module-notice">Enable the {project.module.name} module in your terminal: <code>{project.module.command}</code><span>Your saved files are preserved.</span></div>}
      <div className="session-actions"><Button className="session-run" disabled={disabled || project?.module?.enabled === false} onClick={()=>void action('run')}>{busy==='run'?<LoaderCircle className="spin"/>:<Play/>}{busy==='run'?'Running suite…':'Run tests'}</Button><span><ShieldCheck size={14}/> Tests and feedback use saved files.</span></div>
      <div aria-live="polite" className="session-live">{busy==='coach'?'Your coach is reading the saved project. This can take a few minutes.':busy==='preview'?'Building your saved source…':status?.busy && !busy?'Another exercise operation is running. You can keep editing.':copied?'Copied to clipboard.':''}</div>
      <Tabs value={tab} onValueChange={value=>setTab(String(value))}>
        <TabsList className="session-tabs" variant="line"><TabsTrigger value="brief"><BookOpen/>Brief</TabsTrigger><TabsTrigger value="tests"><Terminal/>Tests{run && <span className={'session-count '+(!run.stale && run.passed?'complete':'')}>{passed}/{run.tests.length}</span>}</TabsTrigger><TabsTrigger value="coach"><ShieldCheck/>Coach</TabsTrigger>{project?.runner==='browser' && <TabsTrigger value="preview"><Eye/>Preview</TabsTrigger>}</TabsList>
        <TabsContent value="brief"><section className="session-section"><div className="session-section-label">THE CHALLENGE</div><p className="session-summary">{project?.summary || 'Your brief will appear here once the local gym connects.'}</p><div className="skill-tags">{project?.skills.map(skill=><span key={skill}>{skill}</span>)}</div><h2>Your finish line</h2><ol className="session-requirements">{project?.requirements.map((requirement,i)=><li key={requirement}><span>{String(i+1).padStart(2,'0')}</span><p>{requirement}</p></li>)}</ol><h2>Keep the docs close</h2><Docs docs={project?.docs || []}/></section></TabsContent>
        <TabsContent value="tests"><section className="session-section"><div className="session-section-label">TEST BENCH</div><h2 className="session-panel-title">{busy==='run'?'Checking your work…':run?.stale?'Time for a fresh run.':run?.passed?'You made it work.':run?'A little closer.':'Find your starting point.'}</h2><p className="session-description">{run?.stale?'Your saved files changed after this run. Run the suite again to check where you stand.':run?.passed?'Every required check passed for this saved version. Take a moment to reflect, or choose your next project.':'Each check describes a part of the contract. A failing test gives you somewhere to look next.'}</p>{run ? <><div className={'session-result '+(run.passed&&!run.stale?'success':'')}><div>{run.passed&&!run.stale?<CheckCircle2/>:<Terminal/>}<strong>{passed} / {run.tests.length}</strong><span>checks passed</span></div><small>{run.elapsed.toFixed(1)}s · {run.stale?'Outdated snapshot':'Saved snapshot'}</small></div><ul className="session-checks">{run.tests.map((test,i)=><li key={test.name+i}><span className={test.action}>{test.action==='pass'?'✓':test.action==='fail'?'×':'−'}</span><code>{test.name}</code><small>{test.action}</small></li>)}</ul><details className="session-output"><summary>Full test output</summary><pre>{run.output || 'No output.'}</pre></details><p className="session-snapshot">Snapshot {run.fingerprint.slice(0,12)}</p></> : <div className="session-empty"><Terminal/><strong>No runs yet</strong><p>Save your first changes, then press Run tests.<br/>You can also run <code>omagym test</code> in your terminal.</p></div>}</section></TabsContent>
        <TabsContent value="coach"><section className="session-section"><div className="session-section-label">REFLECT, THEN TRY AGAIN</div><h2 className="session-panel-title">A second pair of eyes.</h2><p className="session-description">Observations to consider. Questions to work through. Documentation to explore. The implementation stays yours.</p><label className="question-label" htmlFor="session-question">What would you like reviewed? <span>Optional</span></label><textarea id="session-question" className="coach-question" value={question} onChange={e=>setQuestion(e.target.value)} maxLength={2000} placeholder="Am I handling the edge cases consistently?" disabled={!!busy}/><Button className="coach-button" variant="outline" disabled={disabled} onClick={()=>void action('coach')}>{busy==='coach'?<LoaderCircle className="spin"/>:<ShieldCheck/>}{busy==='coach'?'Reading your project…':'Ask for feedback'}</Button><p className="session-privacy">Sends saved project files and the latest tests to your installed Codex only when you ask. No solutions or code edits.</p>{feedback && <article className="session-feedback">{feedback.stale && <p className="session-stale">You’ve saved changes since this review. These observations refer to your earlier code.</p>}{feedback.testFingerprint && feedback.testFingerprint!==feedback.fingerprint && <p className="session-stale">The tests supplied with this review were from an older saved version.</p>}<div className="session-section-label">YOUR REVIEW <time>{new Date(feedback.reviewedAt*1000).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})}</time></div><p>{feedback.feedback}</p>{feedback.observations.length>0 && <><h2>What stands out</h2><ul>{feedback.observations.map(s=><li key={s}>{s}</li>)}</ul></>}{feedback.questions.length>0 && <><h2>Think it through</h2><ul>{feedback.questions.map(s=><li key={s}>{s}</li>)}</ul></>}<h2>Follow the thread</h2><Docs docs={feedback.documentation}/></article>}</section></TabsContent>
        {project?.runner==='browser' && <TabsContent value="preview"><section className="session-section"><div className="session-preview-toolbar"><span>Preview of saved files</span><Button variant="outline" disabled={disabled} onClick={()=>void action('preview')}><RefreshCw size={14}/>{preview?'Rebuild':'Build preview'}</Button></div>{preview && preview.fingerprint!==status?.fingerprint && <p className="session-stale">Saved files changed. Rebuild to update this preview.</p>}{preview ? <><a className="session-preview-link" href={preview.url} target="_blank" rel="noreferrer">Open full preview <ArrowUpRight size={14}/></a><iframe className="session-preview" title="Exercise preview" src={preview.url} sandbox="allow-scripts allow-same-origin allow-forms"/></>:<div className="session-empty"><Eye/><strong>See what you’re building</strong><p>Build your saved source to preview it here.</p></div>}</section></TabsContent>}
      </Tabs>
      <details className="session-files"><summary><FileCode2 size={15}/>{status?.files.length || 0} saved project files</summary><ul>{status?.files.map(file=><li key={file}><code>{file}</code></li>)}</ul></details>
      <div className="session-terminal-tip"><Terminal size={18}/><div><strong>Prefer your terminal?</strong><p><code>omagym brief</code> · <code>omagym test</code> · <code>omagym coach</code></p></div></div>
    </div>
    <footer className="session-footer"><span>Write <ChevronRight/> Test <ChevronRight/> Reflect <ChevronRight/> Repeat</span><a href="/" target="_blank" rel="noreferrer">Project library <ArrowUpRight size={13}/></a></footer>
    <p className="community-notice">Independent community project. Not officially supported or endorsed by DHH or Omacom.</p>
  </main>;
}
