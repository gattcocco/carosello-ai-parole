#!/usr/bin/env python3
# New-wave / coldwave instrumentale, sintetizzato da zero (numpy). 100% originale.
# Am - F - C - G, minore malinconico. Arp + basso + pad + beat sobrio, sidechain.
import numpy as np, wave, struct, sys

SR=44100; BPM=116
beat=60/BPM; bar=4*beat; step=bar/16          # 16 sedicesimi per battuta
# durata totale (s): secondo argomento opzionale, default = v7 (corpo 179,3 + crediti 34)
TOTAL=float(sys.argv[2]) if len(sys.argv)>2 else 213.5
N=int(TOTAL*SR)
rng=np.random.default_rng(7)

def m2f(m): return 440.0*2**((m-69)/12)
def saw(f,n):
    t=np.arange(n)/SR; return 2.0*(t*f-np.floor(0.5+t*f))
def sqr(f,n,duty=0.5):
    t=np.arange(n)/SR; ph=(t*f)%1.0; return np.where(ph<duty,1.0,-1.0)
def sine(f,n): return np.sin(2*np.pi*f*np.arange(n)/SR)
def lp1(x,cut):
    a=np.exp(-2*np.pi*cut/SR); y=np.empty_like(x); acc=0.0
    for i in range(len(x)): acc=(1-a)*x[i]+a*acc; y[i]=acc
    return y
def lp_fast(x,cut):
    # lowpass vettoriale approssimato (filtro a media mobile esponenziale via lfilter manuale)
    a=np.exp(-2*np.pi*cut/SR); b=1-a
    y=np.empty_like(x); acc=0.0
    # loop necessario ma su array corti (una nota per volta)
    for i in range(x.shape[0]): acc=b*x[i]+a*acc; y[i]=acc
    return y
def adsr(n,a,d,s,r):
    a=int(a*SR);d=int(d*SR);r=int(r*SR); a=max(a,1);d=max(d,1);r=max(r,1)
    sus=max(n-a-d-r,0)
    env=np.concatenate([np.linspace(0,1,a),np.linspace(1,s,d),np.full(sus,s),np.linspace(s,0,r)])
    if len(env)<n: env=np.concatenate([env,np.zeros(n-len(env))])
    return env[:n]

buf=np.zeros(N+SR)          # margine
def place(sig,at,gain=1.0):
    s=int(at*SR); e=s+len(sig)
    if s<0: sig=sig[-s:]; s=0
    buf[s:e]+=sig*gain

# ---- voci ----
def synth_note(mid,dur,kind="saw",cut=4000,a=0.005,d=0.08,s=0.7,r=0.12,detune=0.0):
    n=int(dur*SR); f=m2f(mid)
    if kind=="saw":
        x=saw(f,n)
        if detune: x=0.5*x+0.5*saw(f*2**(detune/1200),n)
    elif kind=="sqr": x=sqr(f,n,0.45)
    else: x=sine(f,n)
    x=lp_fast(x,cut)
    return x*adsr(n,a,d,s,r)

def kick(dur=0.28):
    n=int(dur*SR); t=np.arange(n)/SR
    fenv=45+75*np.exp(-t*45)                 # 120->45 Hz
    ph=2*np.pi*np.cumsum(fenv)/SR
    body=np.sin(ph)*np.exp(-t*7.5)
    click=(rng.standard_normal(n)*np.exp(-t*120))*0.15
    return (body+click)*1.1
def snare(dur=0.2):
    n=int(dur*SR); t=np.arange(n)/SR
    noise=rng.standard_normal(n)
    noise=noise-lp_fast(noise,1800)          # highpass ~ noise-lowpass
    tone=np.sin(2*np.pi*185*t)*0.4
    return (noise*0.9+tone)*np.exp(-t*18)
def hat(dur=0.05,open=False):
    n=int(dur*SR); t=np.arange(n)/SR
    noise=rng.standard_normal(n); noise=noise-lp_fast(noise,6000)
    dec=6 if open else 55
    return noise*np.exp(-t*dec)*0.5

# ---- progressione ----
CH={"Am":dict(root=45,arp=[69,72,76],pad=[57,60,64]),
    "F": dict(root=41,arp=[65,69,72],pad=[53,57,60]),
    "C": dict(root=48,arp=[67,72,76],pad=[60,64,67]),
    "G": dict(root=43,arp=[67,71,74],pad=[55,59,62])}
PROG=["Am","F","C","G"]
nbars=int(TOTAL/bar)+1

# tracce separate per fare sidechain e automazioni
arp_buf=np.zeros(N+SR); bass_buf=np.zeros(N+SR); pad_buf=np.zeros(N+SR); drum_buf=np.zeros(N+SR)
def place_into(dst,sig,at,gain=1.0):
    s=int(at*SR)
    if s<0: sig=sig[-s:]; s=0
    e=min(s+len(sig), len(dst))
    if e>s: dst[s:e]+=sig[:e-s]*gain

KICK=[0,4,8,12]; SNARE=[4,12]; HAT=[2,6,10,14]
for b in range(nbars):
    ch=CH[PROG[b%4]]; t0=b*bar
    # pad (accordo sostenuto, caldo, molto filtrato)
    for i,mnote in enumerate(ch["pad"]):
        place_into(pad_buf, synth_note(mnote,bar*0.98,"saw",cut=1400,a=0.15,d=0.3,s=0.85,r=0.4,detune=8), t0, 0.16)
    # basso (ottavi: root/ottava/quinta)
    bpat=[0,12,0,7,0,12,0,7]
    for j,off in enumerate(bpat):
        place_into(bass_buf, synth_note(ch["root"]+off, step*2*0.9,"sqr",cut=900,a=0.004,d=0.06,s=0.6,r=0.06), t0+j*step*2, 0.5)
    # arp (16 sedicesimi che ciclano le note dell'accordo, +ottava a metà giro)
    for s16 in range(16):
        note=ch["arp"][s16%len(ch["arp"])] + (12 if (s16//4)%2 else 0)
        place_into(arp_buf, synth_note(note, step*0.9,"saw",cut=4200,a=0.003,d=0.05,s=0.35,r=0.05), t0+s16*step, 0.28)
    # drums
    for k in KICK:  place_into(drum_buf, kick(), t0+k*step, 0.95)
    for sN in SNARE:place_into(drum_buf, snare(), t0+sN*step, 0.5)
    for h in HAT:   place_into(drum_buf, hat(), t0+h*step, 0.35)

# delay sull'arp (ottavo puntato) — molto new-wave
dl=int(0.75*(60/BPM)*SR)
a=np.zeros_like(arp_buf)
for k,g in [(1,0.34),(2,0.34**2),(3,0.34**3),(4,0.34**4)]:
    d=dl*k
    if d<len(arp_buf): a[d:]+=arp_buf[:-d]*g
arp_buf=0.7*arp_buf+0.6*a

# sidechain: duck di pad+bass a ogni kick
duck=np.ones(len(buf))
kd=int(0.18*SR); shape=1-0.55*np.exp(-np.arange(kd)/(0.05*SR))
for b in range(nbars):
    for k in KICK:
        s=int((b*bar+k*step)*SR)
        duck[s:s+kd]=np.minimum(duck[s:s+kd],shape[:len(duck[s:s+kd])])
pad_buf*=duck; bass_buf*=duck

# automazioni (intro/outro): pad+arp entrano, drums entrano dopo, escono nel finale
def ramp(t_in,t_out,fade=4.0):
    e=np.ones(len(buf))
    a0=int(t_in*SR); e[:a0]=0; e[a0:a0+int(fade*SR)]=np.linspace(0,1,int(fade*SR))
    if t_out is not None:
        o=int(t_out*SR); e[o:o+int(fade*SR)]=np.linspace(1,0,int(fade*SR)); e[o+int(fade*SR):]=0
    return e[:len(buf)]
# uscite ancorate alla fine del brano (con TOTAL=213.5 ridanno i valori della v7)
pad_g =ramp(0.0,TOTAL-6.0,5)
arp_g =ramp(6.0,TOTAL-4.0,5)
bass_g=ramp(12.0,TOTAL-12.0,4)
drum_g=ramp(18.0,TOTAL-20.0,4)          # il beat entra dopo e si ritira sul finale emotivo

mix=pad_buf*pad_g + arp_buf*arp_g + bass_buf*bass_g + drum_buf*drum_g
mix=mix[:N]
# leggero riverbero (delay corti multipli)
rev=mix.copy()
for dt,g in [(0.023,0.22),(0.037,0.17),(0.053,0.12)]:
    d=int(dt*SR); rev[d:]+=mix[:-d]*g
mix=0.85*mix+0.25*rev
# normalizza
mix=mix/np.max(np.abs(mix))*0.89
# stereo: arp/pad leggermente allargati
left=mix.copy(); right=mix.copy()
# write wav 16bit stereo
pcm=np.stack([left,right],axis=1)
pcm16=(np.clip(pcm,-1,1)*32767).astype(np.int16)
out=sys.argv[1] if len(sys.argv)>1 else "newwave.wav"
with wave.open(out,'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm16.tobytes())
print("scritto",out,f"{len(mix)/SR:.1f}s")
