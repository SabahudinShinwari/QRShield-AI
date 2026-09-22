import { useEffect, useRef, useState } from 'react';
import type { ChangeEvent, FormEvent, ReactNode } from 'react';
import {
  Activity, ArrowDownToLine, ArrowRight, BrainCircuit, Camera, Check,
  ChevronRight, CircleAlert, Clipboard, Clock3, Github, History,
  House, Info, KeyRound, LockKeyhole, Menu, Moon, ScanLine, Shield, ShieldAlert,
  ShieldCheck, Sun, Trash2, UploadCloud, X, Eye, EyeOff, Fingerprint, Radar, Sparkles
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

type Page = 'home' | 'dashboard' | 'encrypt' | 'scan' | 'analysis' | 'history' | 'about';
type ActivityRecord = { id: number; action: string; detail: string; time: Date; kind: 'blue' | 'violet' | 'pink' };
type Feedback = { type: 'success' | 'error' | 'info'; message: string } | null;
type URLFinding = { title: string; detail: string; severity: 'attention'|'elevated' };
type URLResult = { hostname:string; scheme:string; caution:'no-obvious-flags'|'review'|'extra-caution'; headline:string; indicators:URLFinding[]; method:string; disclaimer:string; guidance:string };
type MLResult = { signal:'phishing-like'|'benign-like'|'review-required'; method:string; dataset:string; disclaimer:string; review_policy?:string };
const MAX_TEXT_BYTES = 400;
const formatBytes = (s: string) => new TextEncoder().encode(s).length;

async function jsonRequest<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, { cache: 'no-store', ...init });
  const data: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    const msg = typeof data === 'object' && data !== null && 'error' in data && typeof data.error === 'string'
      ? data.error : `Request failed (${response.status}).`;
    throw new Error(msg);
  }
  return data as T;
}

const postJson = <T,>(url: string, body: object) => jsonRequest<T>(url, {
  method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body)
});

function Mark({ small = false }: { small?: boolean }) {
  return <div className={`brand ${small ? 'brand-small' : ''}`}><span className="brand-symbol"><ShieldCheck size={small ? 23 : 27} strokeWidth={2.5}/></span><span>QRShield <strong>AI</strong></span></div>;
}

function Tag({ children, kind = 'blue' }: {children: ReactNode; kind?: 'blue'|'violet'|'pink'|'neutral'}) {
  return <span className={`tag tag-${kind}`}>{children}</span>;
}

function FeedbackLine({ feedback }: { feedback: Feedback }) {
  return feedback ? <div role={feedback.type === 'error' ? 'alert' : 'status'} className={`feedback feedback-${feedback.type}`}>
    {feedback.type === 'error' ? <CircleAlert size={17}/> : <Info size={17}/>}<span>{feedback.message}</span>
  </div> : null;
}

function QRArt({ compact = false }: {compact?: boolean}) {
  const finder = (x: number, y: number) => <g key={`${x}-${y}`}>
    <rect x={x} y={y} width="31" height="31" rx="2" fill="#121c42"/>
    <rect x={x+5} y={y+5} width="21" height="21" rx="1" fill="white"/>
    <rect x={x+10} y={y+10} width="11" height="11" rx="1" fill="#121c42"/>
  </g>;
  return <div className={`qr-decoration ${compact ? 'qr-decoration-small' : ''}`} aria-label="Decorative QR code illustration; not scannable" role="img">
    <svg viewBox="0 0 132 132" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <rect width="132" height="132" rx="11" fill="white"/>
      {Array.from({length: 23 * 23}, (_, i) => {
        const x = i % 23, y = Math.floor(i / 23);
        const inFinder = (x < 7 && y < 7) || (x > 15 && y < 7) || (x < 7 && y > 15);
        return !inFinder && ((x*13+y*19+x*y*7) % 11 < 5)
          ? <rect key={i} x={8+x*5} y={8+y*5} width="4.5" height="4.5" rx="0.3" fill="#121c42"/> : null;
      })}
      {finder(8,8)}{finder(93,8)}{finder(8,93)}
    </svg>
  </div>;
}

const navigation: { id: Page; label: string; icon: LucideIcon }[] = [
  { id: 'dashboard', label: 'Dashboard', icon: House },
  { id: 'encrypt', label: 'Encrypt data', icon: LockKeyhole },
  { id: 'scan', label: 'Scan & decrypt', icon: ScanLine },
  { id: 'analysis', label: 'AI analysis', icon: BrainCircuit },
  { id: 'history', label: 'Session activity', icon: History },
  { id: 'about', label: 'About & security', icon: Info },
];

function Header({ onNavigate, theme, toggleTheme }: { onNavigate:(p:Page)=>void; theme:'light'|'dark'; toggleTheme:()=>void }) {
  return <header className="landing-header">
    <button type="button" className="brand-button" onClick={()=>onNavigate('home')} aria-label="QRShield AI home"><Mark/></button>
    <nav className="landing-nav" aria-label="Primary navigation">
      <button onClick={()=>onNavigate('home')}>Home</button><button onClick={()=>onNavigate('about')}>Features</button>
      <button onClick={()=>onNavigate('about')}>How it works</button><button onClick={()=>onNavigate('about')}>About</button>
    </nav>
    <div className="header-actions">
      <button type="button" className="icon-button theme-on-dark" aria-label="Toggle light or dark workspace" onClick={toggleTheme}>{theme==='light'?<Moon size={19}/>:<Sun size={19}/>}</button>
      <button className="btn btn-primary btn-small" onClick={()=>onNavigate('dashboard')}>Get started <ArrowRight size={16}/></button>
    </div>
  </header>;
}

function Landing({ navigate, theme, toggleTheme }: { navigate:(p:Page)=>void; theme:'light'|'dark'; toggleTheme:()=>void }) {
  return <div className="landing-page">
    <div className="hero-wrap"><Header onNavigate={navigate} theme={theme} toggleTheme={toggleTheme}/>
      <main className="hero max-wrap">
        <div className="hero-text"><div className="eyebrow"><span className="pulse-dot"/> THE QR SECURITY WORKSPACE · VERSION 3.0</div>
          <h1>Secure the message. <span>Question the link.</span></h1>
          <p>A security workspace to encrypt messages, unlock QR codes, and inspect suspicious links before you click. Real cryptography. Transparent URL checks. Optional Gemini explanations.</p>
          <div className="hero-actions"><button className="btn btn-primary" onClick={()=>navigate('encrypt')}>Start encrypting <ArrowRight size={18}/></button>
            <button className="btn btn-ghost" onClick={()=>navigate('about')}>Explore features <ChevronRight size={17}/></button></div>
          <div className="hero-trust"><span><Fingerprint size={19}/> Authenticated encryption</span><span><Radar size={19}/> URL-only inspection</span><span><LockKeyhole size={19}/> Transparent data handling</span></div>
        </div>
        <div className="hero-visual" aria-hidden="true"><div className="visual-orbit orbit-a"/><div className="visual-orbit orbit-b"/>
          <div className="hero-qr-panel"><QRArt/><div className="floating-shield"><Shield size={79} fill="rgba(90,70,236,.2)" strokeWidth={1.4}/><LockKeyhole size={30}/></div></div>
          <div className="float-label label-one"><LockKeyhole size={22}/><span> AES-256-GCM <small>Encryption</small></span></div>
          <div className="float-label label-two"><Radar size={22}/><span> URL inspection <small>Offline rules</small></span></div>
          <div className="float-label label-three"><ScanLine size={22}/><span> QR scanning <small>Available</small></span></div>
        </div>
      </main>
    </div>
    <section className="features-section max-wrap"><div className="section-heading"><div className="eyebrow eyebrow-light">ONE WORKSPACE. CLEAR SECURITY.</div>
      <h2>One workspace. Every critical step.</h2><p>Designed around the moments that matter: protect, decode, investigate.</p></div>
      <div className="features-grid">
        {[
          {name:'Secure encryption', desc:'Password-protect short text using AES-256-GCM and scrypt.', icon: LockKeyhole, kind:'blue', target:'encrypt' as Page},
          {name:'QR code generation', desc:'Preview and download the encrypted QR image instantly.', icon: ScanLine, kind:'violet', target:'encrypt' as Page},
          {name:'Scan & decrypt', desc:'Upload a QR image or use your camera with permission.', icon: Camera, kind:'blue', target:'scan' as Page},
          {name:'URL intelligence lab', desc:'Inspect URL structure offline; train local ML on real data; optionally enable Gemini with consent.', icon: Radar, kind:'pink', target:'analysis' as Page},
        ].map(item=><button key={item.name} className="feature-card" onClick={()=>navigate(item.target)}><span className={`feature-icon icon-${item.kind}`}><item.icon size={24}/></span><h3>{item.name}</h3><p>{item.desc}</p><span className="feature-link">Explore <ArrowRight size={16}/></span></button>)}
      </div>
    </section>
    <section className="journey-section max-wrap" aria-labelledby="journey-title">
      <div className="journey-heading"><span className="section-kicker"><span/> UNDER THE HOOD</span><h2 id="journey-title">Security you can actually understand.</h2><p>No fictional risk scores. No hidden URL requests. Each step tells you exactly what happens to your data.</p></div>
      <div className="journey-track">
        <div className="journey-card"><span className="journey-no">01 / SEAL</span><LockKeyhole size={28}/><h3>Encrypt the content</h3><p>Generate a fresh salt and nonce. Authenticate with AES-256-GCM and turn ciphertext into a QR.</p></div>
        <div className="journey-card"><span className="journey-no">02 / REVEAL</span><ScanLine size={28}/><h3>Scan on your terms</h3><p>Choose an image or grant camera access. Decryption requires the original password.</p></div>
        <div className="journey-card"><span className="journey-no">03 / QUESTION</span><Radar size={28}/><h3>Inspect before visiting</h3><p>Check URL structure without contacting the destination. Run local ML after training, or opt in to a Gemini explanation.</p></div>
      </div>
      <div className="journey-cta"><div><strong>Ready to put it to the test?</strong><span>Try a real encrypted QR from start to finish.</span></div><button className="btn btn-primary" onClick={()=>navigate('encrypt')}>Open the workspace <ArrowRight size={17}/></button></div>
    </section>
    <div className="landing-bottom max-wrap"><div><ShieldCheck size={23}/><span><strong>Real encryption. Transparent limitations.</strong> Educational prototype with a hosted backend.</span></div><button onClick={()=>navigate('about')}>Read security notes <ArrowRight size={16}/></button></div>
    <footer className="footer"><div className="max-wrap footer-inner"><Mark small/><span>Built by Sabahudin Shinwari · QRShield AI v3.0</span><button onClick={()=>navigate('dashboard')}>Open workspace <ArrowRight size={15}/></button></div></footer>
  </div>;
}

function PageTitle({ eyebrow, title, desc }: { eyebrow: string; title: string; desc: string }) {
  return <div className="page-title"><div className="page-eyebrow">{eyebrow}</div><h1>{title}</h1><p>{desc}</p></div>;
}

function Dashboard({ navigate, activity, online, mlReady, refresh }: {navigate:(p:Page)=>void; activity:ActivityRecord[]; online:boolean|null; mlReady:boolean; refresh:()=>void}) {
  const quick: {name:string; desc:string; icon:LucideIcon; page:Page; style:string}[] = [
    {name:'Encrypt data',desc:'Generate an encrypted QR code',icon:LockKeyhole,page:'encrypt',style:'blue'},
    {name:'Scan & decrypt',desc:'Read a QR code securely',icon:ScanLine,page:'scan',style:'violet'},
    {name:'URL intelligence',desc:'Inspect links without opening them',icon:Radar,page:'analysis',style:'pink'},
    {name:'Session history',desc:'Your current tab events only',icon:History,page:'history',style:'blue'},
  ];
  return <><PageTitle eyebrow="YOUR SECURITY CONSOLE" title="Your workspace, your rules." desc="Choose a tool below. Sensitive messages and passwords are not saved in your activity history."/>
    <section className="command-hero"><div className="command-scan"><span className="scan-corners"/><ShieldCheck size={68} strokeWidth={1.15}/><span className="scan-corners scan-corners-b"/></div><div className="command-copy"><span className="command-label"><span/> ENCRYPTION STATION / READY</span><h2>Your content belongs to you.</h2><p>Start with a private message. Generate a protected QR and decrypt it in the same workspace.</p><button className="command-button" onClick={()=>navigate('encrypt')}>Create an encrypted QR <ArrowRight size={17}/></button></div><div className="command-watermark" aria-hidden="true">Q/2</div></section>
    <div className="quick-grid">{quick.map(item=><button className="quick-card" key={item.name} onClick={()=>navigate(item.page)}>
      <div className={`quick-icon icon-${item.style}`}><item.icon size={27}/></div><h3>{item.name}</h3><p>{item.desc}</p><span>Open tool <ArrowRight size={15}/></span></button>)}</div>
    <div className="dashboard-bottom"><section className="panel activity-panel"><div className="panel-head"><div><h2>Recent activity</h2><p>Only events from this tab, without message contents.</p></div><button className="text-button" onClick={()=>navigate('history')}>View all <ArrowRight size={16}/></button></div>
      {activity.length ? <div className="activity-list">{activity.slice(0,4).map(entry=><div className="activity-entry" key={entry.id}><span className={`activity-icon icon-${entry.kind}`}><Check size={18}/></span><div><strong>{entry.action}</strong><small>{entry.detail}</small></div><time>{entry.time.toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})}</time></div>)}</div> : <div className="empty-state"><Clock3 size={32}/><strong>No activity yet</strong><p>When you encrypt or scan, a non-sensitive event appears here for this tab only.</p></div>}
    </section>
    <section className="panel status-panel"><div className="panel-head"><div><h2>System status</h2><p>Live availability, not invented metrics.</p></div></div>
      <div className="status-item"><span className="status-bullet bullet-blue"/><div><strong>Encryption</strong><small>QSE1 / AES-256-GCM / scrypt</small></div><Tag>Implemented</Tag></div>
      <div className="status-item"><span className="status-bullet bullet-violet"/><div><strong>Flask API</strong><small>{online === null ? 'Checking connection' : online ? 'Backend responding' : 'Backend unavailable. Please try again.'}</small></div><Tag kind={online?'blue':'pink'}>{online===null?'Checking':online?'Online':'Offline'}</Tag></div>
      <div className="status-item"><span className="status-bullet bullet-pink"/><div><strong>URL analysis</strong><small>Offline rules · locally trained model optional</small></div><Tag kind="pink">{online===false?'API offline':'Implemented'}</Tag></div>
      <div className="status-item"><span className="status-bullet bullet-violet"/><div><strong>Local ML model</strong><small>{mlReady?'Offline classifier installed':'Not trained yet; see README'}</small></div><Tag kind={mlReady?'violet':'neutral'}>{mlReady?'Ready':'Pending'}</Tag></div>
      <button className="btn btn-outline btn-full" onClick={refresh}>Refresh API status <Activity size={16}/></button>
    </section></div>
    <div className="note-band"><ShieldCheck size={23}/><div><strong>Privacy starts with accurate claims.</strong><span>Messages and passwords are sent to the Flask backend for encryption or decryption. The public website uses a hosted Render backend. URL inspection and ML do not contact the destination website; Gemini explanations are optional and require consent.</span></div></div>
  </>;
}

function EncryptPage({ addActivity, onMoveToScan }: { addActivity:(action:string,detail:string,kind:ActivityRecord['kind'])=>void; onMoveToScan:(payload:string)=>void }) {
  const [message,setMessage] = useState('');
  const [password,setPassword] = useState('');
  const [showPassword,setShowPassword] = useState(false);
  const [qrImage,setQrImage] = useState('');
  const [payload,setPayload] = useState('');
  const [loading,setLoading] = useState(false);
  const [feedback,setFeedback] = useState<Feedback>(null);
  const size = formatBytes(message);
  async function handleSubmit(e:FormEvent) {
    e.preventDefault(); setFeedback(null); setQrImage(''); setPayload('');
    if(size<1 || size>MAX_TEXT_BYTES) {setFeedback({type:'error',message:'Message must contain 1–400 UTF-8 bytes.'}); return;}
    if(!password || formatBytes(password)>1024) {setFeedback({type:'error',message:'Password must contain 1–1024 UTF-8 bytes.'});return;}
    setLoading(true);
    try {
      const result = await postJson<{payload:string;image:string}>('/api/encrypt',{message,password});
      setQrImage(result.image);setPayload(result.payload);
      addActivity('Encrypted QR created','QR PNG generated · no plaintext stored','blue');
      setFeedback({type:'success',message:'Encrypted QR code generated. Download the image and share the password separately over a trusted channel.'});
    } catch(err) {setFeedback({type:'error',message:err instanceof Error?err.message:'Unable to encrypt.'});}
    finally {setLoading(false);}
  }
  async function copyPayload() {
    try { await navigator.clipboard.writeText(payload);setFeedback({type:'success',message:'Encrypted payload copied. It does not contain the password or plaintext.'}); }
    catch {setFeedback({type:'error',message:'Clipboard access was denied. Use the QR PNG download instead.'});}
  }
  return <><PageTitle eyebrow="ENCRYPTION WORKSPACE" title="Encrypt your data" desc="Protect a short message with a password and generate an encrypted QR code using your original cryptographic engine."/>
    <div className="workspace-grid"><section className="panel form-panel"><div className="panel-heading"><span className="panel-icon icon-blue"><LockKeyhole size={21}/></span><div><h2>Message encryption</h2><p>Your message and password are sent to the Flask backend for encryption. On the public website, the backend runs on Render.</p></div></div>
      <form onSubmit={handleSubmit}>
        <label className="field-label" htmlFor="message">Message <span className="optional">Text only · 400 UTF-8 bytes maximum</span></label>
        <textarea id="message" className="field-input message-input" value={message} onChange={e=>setMessage(e.target.value)} placeholder="Write your private message here..." spellCheck={false}/>
        <div className={`byte-counter ${size>MAX_TEXT_BYTES?'byte-over':''}`} aria-live="polite">{size} / {MAX_TEXT_BYTES} bytes</div>
        <label className="field-label" htmlFor="enc-password">Encryption password</label>
        <div className="password-field"><input id="enc-password" className="field-input" type={showPassword?'text':'password'} value={password} onChange={e=>setPassword(e.target.value)} placeholder="Enter a strong password" autoComplete="new-password"/>
          <button type="button" className="input-eye" onClick={()=>setShowPassword(p=>!p)} aria-label={showPassword?'Hide password':'Show password'}>{showPassword?<EyeOff size={19}/>:<Eye size={19}/>}</button></div>
        <p className="field-hint"><Info size={15}/> Choose a long unique password. Weak passwords can be guessed offline from the QR payload.</p>
        <div className="method-line"><span><ShieldCheck size={19}/> Encryption method</span><strong>AES-256-GCM + scrypt</strong></div>
        <FeedbackLine feedback={feedback}/>
        <button type="submit" className="btn btn-primary btn-full action-submit" disabled={loading||size===0||size>MAX_TEXT_BYTES||!password}>
          <LockKeyhole size={18}/>{loading?'Generating encrypted QR…':'Generate secure QR code'}<ArrowRight size={17}/></button>
      </form></section>
      <section className="panel qr-preview-panel"><div className="panel-heading"><span className="panel-icon icon-violet"><ScanLine size={21}/></span><div><h2>QR code preview</h2><p>Your encrypted payload, ready to share.</p></div></div>
        <div className={`qr-preview ${qrImage?'qr-preview-ready':''}`}>
          {qrImage ? <img src={qrImage} alt="Generated encrypted QR code"/> : <><span className="preview-placeholder"><ScanLine size={68} strokeWidth={1.25}/></span><strong>Your QR code appears here</strong><p>Enter a message and password, then generate.</p></>}
        </div>
        {qrImage?<div className="preview-actions"><a className="btn btn-primary btn-full" href={qrImage} download="qrshield_encrypted.png"><ArrowDownToLine size={17}/> Download QR PNG</a>
          <button className="btn btn-outline btn-full" onClick={copyPayload}><Clipboard size={17}/> Copy encrypted payload</button>
          <button className="text-button preview-try" onClick={()=>onMoveToScan(payload)}>Test this QR in decryption <ArrowRight size={16}/></button></div>
          :<button className="btn btn-muted btn-full" disabled><ArrowDownToLine size={17}/> Generate first to download</button>}
        <div className="preview-footnote"><KeyRound size={17}/> Password is never embedded in the QR. Share it separately.</div>
      </section></div></>;
}

function ScanPage({ initialPayload, addActivity, onAnalyzeUrl }: {initialPayload:string; addActivity:(action:string,detail:string,kind:ActivityRecord['kind'])=>void;onAnalyzeUrl:(url:string)=>void}) {
  const [file,setFile] = useState<File|null>(null);
  const [mode,setMode] = useState<'upload'|'camera'>('upload');
  const [payload,setPayload] = useState(initialPayload);
  const [password,setPassword] = useState('');
  const [showPassword,setShowPassword] = useState(false);
  const [result,setResult] = useState('');
  const [visibleResult,setVisibleResult] = useState(true);
  const [scanning,setScanning] = useState(false);
  const [decrypting,setDecrypting] = useState(false);
  const [feedback,setFeedback] = useState<Feedback>(initialPayload?{type:'info',message:'Encrypted payload copied from the Encrypt page. Enter its password below.'}:null);
  const streamRef = useRef<MediaStream|null>(null);
  const videoRef = useRef<HTMLVideoElement|null>(null);
  const fileRef = useRef<HTMLInputElement|null>(null);
  const stopCamera=()=>{
    if(streamRef.current) {streamRef.current.getTracks().forEach(track=>track.stop());streamRef.current=null;}
    if(videoRef.current) videoRef.current.srcObject=null;
  };
  useEffect(()=>()=>{if(streamRef.current)streamRef.current.getTracks().forEach(track=>track.stop());},[]);
  async function startCamera() {
    setMode('camera');setFeedback(null);
    try {
      if (!navigator.mediaDevices?.getUserMedia) throw new Error('Camera unavailable. Use HTTPS or localhost and allow camera access.');
      stopCamera();
      const stream=await navigator.mediaDevices.getUserMedia({video:{facingMode:'environment'},audio:false});
      streamRef.current=stream;
      if(videoRef.current) {videoRef.current.srcObject=stream;await videoRef.current.play();}
      setFeedback({type:'info',message:'Camera ready. Point it at a QR code and select Capture & scan.'});
    } catch(err) {stopCamera();setFeedback({type:'error',message:err instanceof Error?err.message:'Camera unavailable.'});}
  }
  async function scanImage(blob:Blob) {
    setScanning(true);setResult('');setPayload('');setFeedback({type:'info',message:'Uploading image to the Flask backend for scanning…'});
    try {
      const form = new FormData();form.append('image',blob,'qr-image.png');
      const data=await jsonRequest<{payload:string}>('/api/scan',{method:'POST',body:form});
      setPayload(data.payload);addActivity('QR image scanned','Payload extracted · content not logged','violet');
      setFeedback({type:'success',message:data.payload.startsWith('QSE1:')?'Encrypted QR read successfully. Enter the password to decrypt.':'QR read, but it does not use this app’s QSE1 encryption format.'});
    }catch(err){setFeedback({type:'error',message:err instanceof Error?err.message:'Unable to read QR image.'});}
    finally {setScanning(false);}
  }
  async function handleUpload() {
    if(!file){setFeedback({type:'error',message:'Choose a PNG or JPEG image first.'});return;}
    if(file.size>3*1024*1024){setFeedback({type:'error',message:'Image exceeds 3 MB.'});return;}
    await scanImage(file);
  }
  async function captureFrame(){
    const video=videoRef.current;
    if(!video || !video.videoWidth){setFeedback({type:'error',message:'Wait for the camera preview to become ready.'});return;}
    const canvas=document.createElement('canvas');canvas.width=video.videoWidth;canvas.height=video.videoHeight;
    canvas.getContext('2d')?.drawImage(video,0,0);
    const blob=await new Promise<Blob|null>(resolve=>canvas.toBlob(resolve,'image/png'));
    if(blob) await scanImage(blob);else setFeedback({type:'error',message:'Failed to capture camera frame.'});
  }
  async function handleDecrypt(e:FormEvent){
    e.preventDefault();setResult('');setFeedback(null);
    if(!payload.startsWith('QSE1:')){setFeedback({type:'error',message:'This is not a supported QSE1 encrypted QR payload.'});return;}
    if(!password){setFeedback({type:'error',message:'Enter the decryption password.'});return;}
    setDecrypting(true);
    try {
      const data=await postJson<{message:string}>('/api/decrypt',{payload,password});setResult(data.message);setVisibleResult(true);
      addActivity('Message decrypted','Authentication successful · text not logged','blue');
      setFeedback({type:'success',message:'Authenticated decryption succeeded. The recovered message is shown below.'});
    }catch(err){setFeedback({type:'error',message:err instanceof Error?err.message:'Decryption failed.'});}
    finally {setDecrypting(false);}
  }
  function onChangeFile(e:ChangeEvent<HTMLInputElement>){const selected=e.target.files?.[0]??null;setFile(selected);setFeedback(null);}
  return <><PageTitle eyebrow="QR SCANNER" title="Scan & decrypt" desc="Upload a QR image, use your camera, or paste a QSE1 payload to recover encrypted text."/>
    <div className="scan-layout"><section className="panel scan-panel"><div className="panel-heading"><span className="panel-icon icon-violet"><ScanLine size={21}/></span><div><h2>Scan a QR code</h2><p>Camera permission is requested only when you start it.</p></div></div>
      <div className="tab-bar" role="group" aria-label="Scanner input method"><button className={mode==='upload'?'active':''} onClick={()=>{stopCamera();setMode('upload');}}><UploadCloud size={17}/> Upload image</button>
        <button className={mode==='camera'?'active':''} onClick={()=>{setMode('camera');setFeedback(null);}}><Camera size={17}/> Use camera</button></div>
      {mode==='upload'?<><input ref={fileRef} type="file" accept=".png,.jpg,.jpeg,image/png,image/jpeg" onChange={onChangeFile} className="visually-hidden" id="qr-image-input"/>
        <button className="upload-drop" onClick={()=>fileRef.current?.click()}><span><UploadCloud size={36}/></span><strong>{file?file.name:'Choose a QR code image'}</strong><small>{file?`${(file.size/1024).toFixed(1)} KB · click to replace`:'PNG or JPG/JPEG · up to 3 MB'}</small></button>
        <button className="btn btn-primary btn-full" disabled={!file||scanning} onClick={handleUpload}><ScanLine size={18}/>{scanning?'Scanning…':'Scan selected image'}</button></>
        :<><div className="camera-box"><video ref={videoRef} playsInline muted autoPlay aria-label="Live camera preview"/><span>Camera preview</span></div>
        <div className="camera-actions"><button className="btn btn-outline" onClick={startCamera}><Camera size={17}/> Start camera</button><button className="btn btn-primary" onClick={captureFrame} disabled={!streamRef.current||scanning}><ScanLine size={17}/> Capture & scan</button><button className="btn btn-muted" onClick={()=>{stopCamera();setFeedback({type:'info',message:'Camera stopped.'});}}>Stop</button></div></>}
      <div className="small-note"><Info size={17}/> Only PNG/JPEG files are accepted. QR images are uploaded to the Flask backend for scanning.</div>
    </section>
    <section className="panel decrypt-panel"><div className="panel-heading"><span className="panel-icon icon-blue"><KeyRound size={21}/></span><div><h2>Decrypt QR data</h2><p>Requires a QSE1 payload and the correct password.</p></div></div>
      <form onSubmit={handleDecrypt}><label className="field-label" htmlFor="payload">Encrypted QR payload <span className="optional">Pasted or extracted</span></label>
        <textarea id="payload" className="field-input payload-input" placeholder="Scan a QR or paste QSE1:{...}" value={payload} onChange={e=>{setPayload(e.target.value);setResult('');}} spellCheck={false}/>
        <label className="field-label" htmlFor="dec-password">Decryption password</label><div className="password-field"><input id="dec-password" className="field-input" type={showPassword?'text':'password'} value={password} onChange={e=>setPassword(e.target.value)} autoComplete="current-password" placeholder="Enter the original password"/>
          <button type="button" className="input-eye" aria-label={showPassword?'Hide password':'Show password'} onClick={()=>setShowPassword(s=>!s)}>{showPassword?<EyeOff size={19}/>:<Eye size={19}/>}</button></div>
        <FeedbackLine feedback={feedback}/><button className="btn btn-primary btn-full action-submit" disabled={decrypting||!payload||!password} type="submit"><LockKeyhole size={18}/>{decrypting?'Decrypting…':'Decrypt securely'}<ArrowRight size={17}/></button></form>
      {result&&<div className="result-box"><div><strong>Recovered message</strong><button className="text-button" onClick={()=>setVisibleResult(v=>!v)}>{visibleResult?<EyeOff size={16}/>:<Eye size={16}/>} {visibleResult?'Hide':'Show'}</button></div>
        <p>{visibleResult?result:'••••••••••••••••'}</p><div className="recovered-actions"><button className="btn btn-outline" onClick={()=>{setResult('');setPassword('');setFeedback({type:'info',message:'Recovered message and password cleared from the form.'});}}>Clear result <Trash2 size={16}/></button>
        {/***** No automatic URL submission. Only show for a complete URL. *****/}
        {/^(https?:\/\/)[^\s]+$/i.test(result.trim())&&<button className="btn btn-primary" onClick={()=>onAnalyzeUrl(result.trim())}><Radar size={16}/> Inspect this URL <ArrowRight size={15}/></button>}</div></div>}
    </section></div></>;
}

function AnalysisPage({ initialUrl, addActivity, geminiReady, mlReady }: {
  initialUrl:string;
  addActivity:(action:string,detail:string,kind:ActivityRecord['kind'])=>void;
  geminiReady:boolean;
  mlReady:boolean;
}) {
  const [url,setUrl] = useState(initialUrl);
  const [result,setResult] = useState<URLResult|null>(null);
  const [checking,setChecking] = useState(false);
  const [feedback,setFeedback] = useState<Feedback>(initialUrl?{type:'info',message:'URL transferred locally from the decrypted message. Inspection starts only if you click Inspect URL.'}:null);
  const [consent,setConsent] = useState(false);
  const [explanation,setExplanation] = useState('');
  const [explaining,setExplaining] = useState(false);
  const [mlResult,setMlResult] = useState<MLResult|null>(null);
  const [mlWorking,setMlWorking] = useState(false);
  const changeUrl=(value:string)=>{setUrl(value);setResult(null);setExplanation('');setConsent(false);setMlResult(null);setFeedback(null);};
  async function inspect(e:FormEvent){
    e.preventDefault();setChecking(true);setResult(null);setExplanation('');setConsent(false);setMlResult(null);setFeedback(null);
    try {
      const data=await postJson<URLResult>('/api/analyze',{url:url.trim()});
      setResult(data);addActivity('URL structure inspected','Structural checks completed · no URL stored in tab history','pink');
      setFeedback({type:'info',message:'Inspected by the Flask backend. No request was sent to the destination website.'});
    } catch(err) {setFeedback({type:'error',message:err instanceof Error?err.message:'Unable to inspect the URL.'});}
    finally {setChecking(false);}
  }
  async function runLocalMl(){
    if(!result||!mlReady) return;
    setMlWorking(true);setMlResult(null);setFeedback(null);
    try {
      const data=await postJson<MLResult>('/api/ml/predict',{url:url.trim()});
      setMlResult(data);
      addActivity('Local ML pattern checked','Server-side model inference · no URL stored in tab history','violet');
    } catch(err) {setFeedback({type:'error',message:err instanceof Error?err.message:'Local ML unavailable.'});}
    finally {setMlWorking(false);}
  }
  async function askGemini(){
    if(!result||!consent||!geminiReady) return;
    setExplaining(true);setExplanation('');setFeedback(null);
    try {
      const data=await postJson<{explanation:string;provider:string;shared:string}>('/api/ai/explain',{url:url.trim(),consent:true});
      setExplanation(data.explanation);
      addActivity('AI explanation generated','User opted in · no URL or prompt saved in activity','violet');
    } catch(err) {setFeedback({type:'error',message:err instanceof Error?err.message:'Gemini explanation failed.'});}
    finally {setExplaining(false);}
  }
  const statusLabel=result?.caution==='extra-caution'?'EXTRA CAUTION':result?.caution==='review'?'REVIEW ADVISED':'NO OBVIOUS FLAGS';
  return <>
    <PageTitle eyebrow="THREAT INTELLIGENCE / LOCAL FIRST" title="Inspect the link. Not the risk." desc="Inspect URL-only rules and optionally run a trained classifier on the Flask backend. Neither proves a link is safe."/>
    <div className="intelligence-intro"><div><span className="command-label"><span/> URL INTELLIGENCE LAB</span><h2>The safest click is the one you question first.</h2><p>Paste a suspicious QR link below. The Flask backend checks its structure without contacting the destination, following redirects, or downloading anything.</p><div className="intelligence-chips"><span><Radar size={14}/> No destination visits</span><span><Fingerprint size={14}/> No URL in tab history</span><span><ShieldCheck size={14}/> No invented accuracy</span></div></div><div className="intelligence-visual" aria-hidden="true"><div className="radar-outer"><div className="radar-inner"><Radar size={66} strokeWidth={1.15}/></div></div><span className="radar-caption">INSPECT / DON'T VISIT</span></div></div>
    <div className="analysis-grid"><section className="panel analysis-entry"><div className="panel-heading"><span className="panel-icon icon-blue"><Radar size={21}/></span><div><h2>Inspect a URL</h2><p>Enter one complete HTTPS or HTTP address.</p></div></div>
      <form onSubmit={inspect}><label className="field-label" htmlFor="inspection-url">URL to inspect</label><div className="url-input-wrap"><input id="inspection-url" className="field-input" type="text" inputMode="url" spellCheck={false} autoComplete="off" value={url} maxLength={2048} onChange={e=>changeUrl(e.target.value)} placeholder="https://example.org/page"/><Radar size={19}/></div>
      <p className="field-hint"><Info size={15}/> This tool does not visit the URL or verify its owner. Results are structural indicators, not a security verdict.</p>
      <FeedbackLine feedback={feedback}/><button className="btn btn-primary btn-full action-submit" type="submit" disabled={!url.trim()||checking}><Radar size={18}/>{checking?'Inspecting URL…':'Inspect URL structure'}<ArrowRight size={17}/></button></form>
      <div className="analysis-examples"><span>Try examples</span><button type="button" onClick={()=>changeUrl('https://example.org/docs')}>Regular HTTPS</button><button type="button" onClick={()=>changeUrl('http://account.example.org@192.0.2.10/login')}>Disguised host</button></div>
    </section>
    <aside className="panel analysis-method"><span className="method-no">01—03 / METHODOLOGY</span><h2>Evidence, not illusion.</h2><div className="method-step"><span>01</span><div><strong>Parse</strong><p>Validate the scheme, hostname and URL syntax.</p></div></div><div className="method-step"><span>02</span><div><strong>Inspect</strong><p>Apply explainable structural rules; optionally run a trained URL-only model.</p></div></div><div className="method-step"><span>03</span><div><strong>Interpret</strong><p>Review indicators. Opt in to AI explanation if configured.</p></div></div><div className="method-footer"><ShieldAlert size={20}/><p>No live blacklist or certificate validation. The classifier only runs after dataset training and is not a safety guarantee.</p></div></aside></div>
    {result&&<section className="panel findings-panel" aria-live="polite"><div className="findings-top"><div><span className="section-kicker"><span/> STRUCTURE INSPECTION COMPLETE</span><h2>{result.headline}</h2><p>Inspected hostname: <strong>{result.hostname}</strong> · Scheme: {result.scheme.toUpperCase()}</p></div><span className={`risk-label risk-${result.caution}`}><ShieldAlert size={16}/>{statusLabel}</span></div>
      <div className="findings-list">{result.indicators.length?result.indicators.map((f,i)=><div className="finding-item" key={`${f.title}-${i}`}><span className={`finding-symbol severity-${f.severity}`}><CircleAlert size={19}/></span><div><strong>{f.title}</strong><p>{f.detail}</p></div><Tag kind={f.severity==='elevated'?'pink':'violet'}>{f.severity==='elevated'?'Extra caution':'Review'}</Tag></div>):<div className="finding-empty"><Info size={24}/><div><strong>No listed indicators matched.</strong><p>A malicious link can still appear entirely ordinary. Confirm the sender and destination independently.</p></div></div>}</div>
      <div className="finding-notice"><ShieldAlert size={21}/><div><strong>Not a verdict.</strong><p>{result.disclaimer} {result.guidance}</p></div></div>
      <div className="ml-zone"><div className="gemini-heading"><span className="ai-orb"><BrainCircuit size={20}/></span><div><h3>Server-side machine-learning check</h3><p>Train a URL-only phishing-pattern classifier on the UCI dataset. Inference runs on the Flask backend (hosted on Render for the public website), without visiting the destination or sending the URL to an AI provider.</p></div><Tag kind={mlReady?'violet':'neutral'}>{mlReady?'Model installed':'Training required'}</Tag></div>
        {mlReady?<button type="button" className="btn btn-primary" disabled={mlWorking} onClick={runLocalMl}><BrainCircuit size={17}/>{mlWorking?'Running ML model…':'Analyze with ML'}<ArrowRight size={16}/></button>:<p className="setup-hint">The model is not available to this backend. Check the model artifact and API health endpoint. No predictions are fabricated.</p>}
        {mlResult&&<div className="ml-result" role="status"><div className="ml-result-label"><BrainCircuit size={20}/><strong>Model signal: {mlResult.signal==='review-required'?'Manual review required — borderline model signal':mlResult.signal==='phishing-like'?'Phishing-like URL pattern':'Benign-like URL pattern'}</strong></div><p>{mlResult.disclaimer}</p>{mlResult.review_policy&&<p>{mlResult.review_policy}</p>}<small>{mlResult.method} Dataset: {mlResult.dataset}. No probability displayed.</small></div>}
      </div>
      <div className="gemini-zone"><div className="gemini-heading"><span className="ai-orb"><Sparkles size={20}/></span><div><h3>Ask Gemini to explain the findings</h3><p>Optional. Gemini can explain these rules, but cannot prove whether a link is safe.</p></div><Tag kind={geminiReady?'violet':'neutral'}>{geminiReady?'Key present · access unverified':'Setup required'}</Tag></div>
      <label className="consent-row"><input type="checkbox" checked={consent} onChange={e=>setConsent(e.target.checked)} disabled={!geminiReady}/><span>I agree to share this link’s <strong>hostname, scheme and findings</strong> with Google Gemini. No full URL, path, query, message or password is sent.</span></label>
      <button type="button" className="btn btn-primary" onClick={askGemini} disabled={!geminiReady||!consent||explaining}><Sparkles size={17}/>{explaining?'Requesting explanation…':'Generate AI explanation'}<ArrowRight size={16}/></button>
      {!geminiReady&&<p className="setup-hint">To enable: set GEMINI_API_KEY on the Flask backend, restart it and refresh this page. Never put an API key in React or GitHub.</p>}
      {explanation&&<div className="explanation-box" role="status"><span><Sparkles size={17}/> AI-generated explanation</span><p>{explanation}</p><small>Provider: Gemini · AI text can be mistaken; independently verify the destination.</small></div>}
      </div>
    </section>}
  </>;
}

function HistoryPage({ activity, clear }: {activity:ActivityRecord[];clear:()=>void}) {
  return <><PageTitle eyebrow="IN-MEMORY EVENTS" title="Session activity" desc="Activity labels are kept in memory in this browser tab. Hosting and backend logs are separate."/>
    <section className="panel history-panel"><div className="panel-head"><div><h2>Activity in this tab</h2><p>Refresh or close the tab to clear all entries automatically.</p></div><button className="btn btn-outline" disabled={!activity.length} onClick={clear}><Trash2 size={17}/> Clear events</button></div>
      {activity.length?activity.map(a=><div className="history-entry" key={a.id}><span className={`activity-icon icon-${a.kind}`}><History size={19}/></span><div><strong>{a.action}</strong><small>{a.detail}</small></div><time>{a.time.toLocaleTimeString()}</time></div>)
        :<div className="empty-state big-empty"><History size={37}/><strong>Nothing to display yet</strong><p>Encrypt or scan a QR code to add an event. We never store your password or message in this history.</p></div>}
    </section></>;
}

function AboutPage({ navigate }: {navigate:(p:Page)=>void}) {
  return <><PageTitle eyebrow="ABOUT THE PROJECT" title="Designed for useful security" desc="A transparent, educational QR encryption demo rebuilt with a professional interface."/>
    <div className="about-grid"><section className="panel about-main"><h2>How QRShield works</h2>
      <div className="step"><span>01</span><div><h3>Encrypt your message</h3><p>Your browser sends the password and short message to the Flask backend (hosted on Render when using the public website). A random salt and nonce are generated, a key is derived with scrypt, and AES-256-GCM authenticates and encrypts the data.</p></div></div>
      <div className="step"><span>02</span><div><h3>Create a QR image</h3><p>A versioned QSE1 payload stores the salt, nonce, and ciphertext with authentication tag. The password and message are not serialized in the QR code.</p></div></div>
      <div className="step"><span>03</span><div><h3>Scan and decrypt</h3><p>Upload a PNG/JPEG, capture a webcam image, or paste the payload; then enter the password. Wrong passwords or modified ciphertext fail authenticated decryption.</p></div></div>
      <button className="btn btn-primary" onClick={()=>navigate('encrypt')}>Try the encryption flow <ArrowRight size={17}/></button>
    </section><aside className="panel about-side"><ShieldCheck size={35}/><h2>Important limitations</h2><ul>
      <li>Educational prototype with public hosting; not independently security-audited.</li><li>Passwords can be attacked offline; choose a strong one.</li><li>No built-in safe password sharing or sender identity verification.</li><li>Neither QR scanning nor AES-GCM detects phishing.</li><li>URL rules are heuristics; the separate model was trained and evaluated on the UCI dataset. Neither is a reputation service or safety verdict.</li><li>Gemini explanation is optional and requires configuration and explicit consent.</li><li>Public hosting is provided for demonstration; there are no user accounts, guaranteed persistent history, or independently audited production security controls.</li>
    </ul><div className="about-author"><strong>Built by Sabahudin Shinwari</strong><span>Computer Science (Data Science), Albukhary International University</span><a href="https://github.com/SabahudinShinwari" target="_blank" rel="noreferrer"><Github size={17}/> GitHub profile</a></div></aside></div></>;
}

function App() {
  const [page,setPage] = useState<Page>('home');
  const [theme,setTheme] = useState<'light'|'dark'>(()=>{
    try {return localStorage.getItem('qrshield-theme')==='dark'?'dark':'light';}catch{return 'light';}
  });
  const [menuOpen,setMenuOpen]=useState(false);
  const [activity,setActivity]=useState<ActivityRecord[]>([]);
  const [online,setOnline]=useState<boolean|null>(null);
  const [geminiReady,setGeminiReady]=useState(false);
  const [mlReady,setMlReady]=useState(false);
  const [incomingUrl,setIncomingUrl]=useState('');
  const [analysisKey,setAnalysisKey]=useState(0);
  const [incomingPayload,setIncomingPayload]=useState('');
  const [scanKey,setScanKey]=useState(0);
  function navigate(p:Page){setPage(p);setMenuOpen(false);window.scrollTo({top:0,behavior:'instant'});}
  function toggleTheme(){setTheme(t=>{const next=t==='light'?'dark':'light';try{localStorage.setItem('qrshield-theme',next);}catch{/* storage may be blocked */}return next;});}
  function addActivity(action:string,detail:string,kind:ActivityRecord['kind']){
    setActivity(prev=>[{id:Date.now()+Math.random(),action,detail,kind,time:new Date()},...prev].slice(0,20));
  }
  function moveToScan(payload:string){setIncomingPayload(payload);setScanKey(k=>k+1);navigate('scan');}
  function moveToAnalysis(url:string){setIncomingUrl(url);setAnalysisKey(k=>k+1);navigate('analysis');}
  async function checkHealth(){setOnline(null);try{const data=await jsonRequest<{status:string;gemini_explanations:string;ml?:{ready:boolean}}>('/api/health');setOnline(data.status==='ok');setGeminiReady(data.gemini_explanations==='configured');setMlReady(data.ml?.ready===true);}catch{setOnline(false);setGeminiReady(false);setMlReady(false);}}
  useEffect(()=>{void checkHealth();},[]);
  const current=navigation.find(n=>n.id===page);
  return <div className={`app ${theme==='dark'?'dark':''}`}>
    {page==='home'?<Landing navigate={navigate} theme={theme} toggleTheme={toggleTheme}/>:<div className="workspace">
      <aside className={`sidebar ${menuOpen?'sidebar-open':''}`}><div className="sidebar-top"><button onClick={()=>navigate('home')} className="brand-button"><Mark small/></button><button className="mobile-only icon-button" onClick={()=>setMenuOpen(false)} aria-label="Close menu"><X size={23}/></button></div>
        <div className="sidebar-label">WORKSPACE</div><nav aria-label="Workspace navigation" className="sidebar-nav">{navigation.map(n=><button key={n.id} aria-current={page===n.id?'page':undefined} className={page===n.id?'active':''} onClick={()=>navigate(n.id)}><n.icon size={19}/><span>{n.label}</span>{page===n.id&&<span className="nav-line"/>}</button>)}</nav>
        <div className="sidebar-bottom"><div className="sidebar-help"><ShieldCheck size={28}/><strong>Security first</strong><p>Encryption you can inspect. AI claims you can verify.</p><button onClick={()=>navigate('about')}>Read more <ArrowRight size={14}/></button></div>
          <div className="sidebar-credit">QRShield AI <span>v3.0 · Educational prototype</span></div></div>
      </aside>
      {menuOpen&&<button className="mobile-overlay" aria-label="Close navigation" onClick={()=>setMenuOpen(false)}/>}
      <div className="main-column"><header className="workspace-header"><div className="breadcrumb"><button className="mobile-menu icon-button" aria-label="Open navigation" onClick={()=>setMenuOpen(true)}><Menu size={22}/></button><span className="breadcrumb-icon">{current&&<current.icon size={18}/>}</span><span>{current?.label??'Workspace'}</span></div>
        <div className="workspace-head-right"><div className="connection" title={online===null?'Checking backend':online?'Flask API available':'Flask API unavailable'}><span className={`connection-dot ${online?'connected':''}`}/>{online?'API online':online===null?'Connecting…':'API offline'}</div>
          <button className="icon-button theme-button" onClick={toggleTheme} aria-label="Toggle workspace theme">{theme==='light'?<Moon size={18}/>:<Sun size={18}/>}</button>
          <div className="profile-chip"><div>S</div><span>Sabahudin <small>Developer</small></span></div></div>
      </header><main className="workspace-content">
        {page==='dashboard'&&<Dashboard navigate={navigate} activity={activity} online={online} mlReady={mlReady} refresh={()=>void checkHealth()}/>}
        {page==='encrypt'&&<EncryptPage addActivity={addActivity} onMoveToScan={moveToScan}/>}
        {page==='scan'&&<ScanPage key={scanKey} initialPayload={incomingPayload} addActivity={addActivity} onAnalyzeUrl={moveToAnalysis}/>}
        {page==='analysis'&&<AnalysisPage key={analysisKey} initialUrl={incomingUrl} addActivity={addActivity} geminiReady={geminiReady} mlReady={mlReady}/>}
        {page==='history'&&<HistoryPage activity={activity} clear={()=>setActivity([])}/>}
        {page==='about'&&<AboutPage navigate={navigate}/>}
      </main><footer className="workspace-footer"><span><ShieldCheck size={17}/> QRShield AI · Educational hosted prototype</span><span>Made by Sabahudin Shinwari</span></footer></div></div>}
  </div>;
}

export default App;
