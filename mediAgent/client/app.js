const { useState, useEffect } = React;

function App() {
    const [page, setPage] = useState('intake'); // intake, thinking, result
    const [inputs, setInputs] = useState({
        age: 45,
        chief_complaint: 'Headache',
        vitals: { hr: 80, rr: 16, bp_sys: 120, o2: 98, temp: 37 }
    });
    const [result, setResult] = useState(null);
    const [logs, setLogs] = useState([]);

    const handleRun = () => {
        setPage('thinking');
        setLogs([]);

        // Simulate Thinking Steps
        const steps = [
            "🔍 Step 1: Understanding Context & Data Completeness...",
            "🧠 Step 2: Analyzing Risk Factors (Heart, Lungs, BP)...",
            "⚖️ Step 3: Self-Evaluating Confidence Score...",
            "🚪 Step 4: Decision Gate & Safety Checks...",
            "🤖 Step 5: Generating Care Plan..."
        ];

        let i = 0;
        const interval = setInterval(() => {
            if (i < steps.length) {
                setLogs(prev => [...prev, steps[i]]);
                i++;
            } else {
                clearInterval(interval);
                // Run Logic
                const res = window.TriageAgent.deliberate(inputs);
                if (res.decision === "ACT") {
                    res.plan = window.TriageAgent.generateCarePlan(inputs);
                }
                res.address = inputs.address || "Address not provided";
                setResult(res);
                setTimeout(() => setPage('result'), 800);
            }
        }, 800);
    };

    return (
        <div className="max-w-4xl mx-auto p-6">
            <header className="mb-8 flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
                        <span className="text-blue-600">Medi</span>Agent
                    </h1>
                    <p className="text-slate-500 font-medium">Autonomous Triage System (S2)</p>
                </div>
                <div className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">
                    Agent Active
                </div>
            </header>

            <main>
                {page === 'intake' && (
                    <IntakeForm inputs={inputs} setInputs={setInputs} onRun={handleRun} />
                )}

                {page === 'thinking' && (
                    <ThinkingProcess logs={logs} />
                )}

                {page === 'result' && result && (
                    <ResultView result={result} onReset={() => setPage('intake')} />
                )}
            </main>
        </div>
    );
}

function IntakeForm({ inputs, setInputs, onRun }) {
    const handleChange = (field, val) => {
        setInputs({ ...inputs, [field]: val });
    };
    const handleVital = (field, val) => {
        setInputs({ ...inputs, vitals: { ...inputs.vitals, [field]: parseInt(val) } });
    };

    return (
        <div className="glass card-shadow rounded-2xl p-8 bg-white animate-enter">
            <h2 className="text-xl font-bold mb-6 text-slate-800">Patient Intake</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div>
                    <label className="block text-sm font-semibold text-slate-600 mb-2">Age</label>
                    <input type="number" className="w-full p-3 border rounded-lg bg-slate-50 focus:ring-2 focus:ring-blue-500 outline-none"
                        value={inputs.age} onChange={e => handleChange('age', e.target.value)} />
                </div>
                <div>
                    <label className="block text-sm font-semibold text-slate-600 mb-2">Chief Complaint</label>
                    <select className="w-full p-3 border rounded-lg bg-slate-50 focus:ring-2 focus:ring-blue-500 outline-none"
                        value={inputs.chief_complaint} onChange={e => handleChange('chief_complaint', e.target.value)}>
                        <option>Headache</option>
                        <option>Chest Pain</option>
                        <option>Fever</option>
                        <option>Shortness of Breath</option>
                        <option>Other</option>
                    </select>
                    {inputs.chief_complaint === "Other" && (
                        <input type="text" placeholder="Specify complaint..." className="mt-2 w-full p-3 border rounded-lg bg-slate-50 animate-enter outline-none"
                            value={inputs.other_complaint || ""} onChange={e => handleChange('other_complaint', e.target.value)} />
                    )}
                </div>
                <div>
                    <label className="block text-sm font-semibold text-slate-600 mb-2">Symptom Severity (0-10)</label>
                    <input type="range" min="0" max="10" className="w-full accent-blue-600"
                        value={inputs.severity || 5} onChange={e => handleChange('severity', e.target.value)} />
                    <div className="text-right text-sm font-bold text-blue-600">{inputs.severity || 5}/10</div>
                </div>
                <div>
                    <label className="block text-sm font-semibold text-slate-600 mb-2">Duration</label>
                    <input type="text" placeholder="e.g. 2 days" className="w-full p-3 border rounded-lg bg-slate-50 outline-none"
                        value={inputs.duration || ""} onChange={e => handleChange('duration', e.target.value)} />
                </div>
                <div className="md:col-span-2">
                    <label className="block text-sm font-semibold text-slate-600 mb-2">Delivery Address (for medicines)</label>
                    <input type="text" placeholder="Enter your address for medicine delivery" className="w-full p-3 border rounded-lg bg-slate-50 outline-none"
                        value={inputs.address || ""} onChange={e => handleChange('address', e.target.value)} />
                </div>
            </div>

            <div className="my-6">
                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4">Vital Signs</h3>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                    <VitalInput label="HR (bpm)" val={inputs.vitals.hr} change={v => handleVital('hr', v)} />
                    <VitalInput label="RR (bpm)" val={inputs.vitals.rr} change={v => handleVital('rr', v)} />
                    <VitalInput label="Sys BP" val={inputs.vitals.bp_sys} change={v => handleVital('bp_sys', v)} />
                    <VitalInput label="O2 (%)" val={inputs.vitals.o2} change={v => handleVital('o2', v)} />
                    <VitalInput label="Temp (°C)" val={inputs.vitals.temp} change={v => handleVital('temp', v)} />
                </div>
            </div>

            <button onClick={onRun} className="w-full py-4 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl shadow-lg transform transition active:scale-95 text-lg flex items-center justify-center gap-2">
                <span>Run Logic</span>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
            </button>
        </div>
    );
}

function VitalInput({ label, val, change }) {
    return (
        <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
            <label className="block text-xs font-bold text-slate-500 mb-1">{label}</label>
            <input type="number" className="w-full bg-transparent font-mono font-bold text-lg outline-none"
                value={val} onChange={e => change(e.target.value)} />
        </div>
    );
}

function ThinkingProcess({ logs }) {
    return (
        <div className="glass card-shadow rounded-2xl p-8 bg-white min-h-[400px] flex flex-col justify-center items-center">
            <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mb-8"></div>
            <div className="space-y-4 w-full max-w-md">
                {logs.map((log, i) => (
                    <div key={i} className="flex items-center gap-3 text-slate-600 animate-enter" style={{ animationDelay: `${i * 0.1}s` }}>
                        <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                        <p className="font-medium">{log}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}

function ResultView({ result, onReset }) {
    const isRisky = result.decision.includes("REFUSE");
    const color = isRisky ? "bg-red-500" : "bg-emerald-500";
    const bg = isRisky ? "bg-red-50" : "bg-emerald-50";

    // Auto-scroll to top
    useEffect(() => { window.scrollTo(0, 0); }, []);

    return (
        <div className="space-y-6 animate-enter">
            {/* Main Decision Card */}
            <div className={`${color} text-white p-8 rounded-2xl shadow-xl flex items-center gap-6`}>
                <div className="text-5xl">{isRisky ? "🛑" : "✅"}</div>
                <div>
                    <h2 className="text-3xl font-bold">{result.decision.replace(/_/g, " ")}</h2>
                    <p className="opacity-90 text-lg mt-1">{result.reason}</p>
                </div>
            </div>

            {/* Doctor Call Action (High Risk) */}
            {result.shouldCallDoctor && (
                <div className="bg-red-50 border border-red-200 p-6 rounded-2xl flex items-center justify-between shadow-lg animate-pulse">
                    <div className="flex items-center gap-4">
                        <div className="bg-red-100 p-3 rounded-full"><span className="text-3xl">🚑</span></div>
                        <div>
                            <h3 className="font-bold text-red-800 text-xl">Calling Emergency Services...</h3>
                            <p className="text-red-600">Connecting to Dr. Smith (On-Call)</p>
                        </div>
                    </div>
                    <button className="bg-red-600 text-white px-6 py-2 rounded-lg font-bold shadow-md">Connecting...</button>
                </div>
            )}

            {/* Doctor Consultation Card */}
            <div className="bg-blue-50 border border-blue-200 p-6 rounded-2xl shadow-md">
                <div className="flex items-center justify-between">
                    <div>
                        <h3 className="font-bold text-blue-800 text-lg">Need Medical Consultation?</h3>
                        <p className="text-blue-600 text-sm">24/7 Telemedicine Available</p>
                    </div>
                    <div className="text-right">
                        <p className="text-xs text-blue-500 uppercase font-semibold">Call Now</p>
                        <p className="text-2xl font-bold text-blue-700">1-800-MED-HELP</p>
                        <p className="text-sm text-blue-600">(1-800-633-4357)</p>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <MetricCard label="Confidence" val={result.metrics.confidence.toFixed(0) + "%"} />
                <MetricCard label="Risk Level" val={result.metrics.riskSeverity.toFixed(0) + "%"} />
                <MetricCard label="Data Integrity" val={result.metrics.completeness.toFixed(0) + "%"} />
            </div>

            {/* Condition Status Card */}
            <div className={`p-6 rounded-2xl shadow-lg ${result.metrics.riskSeverity > 70 ? 'bg-red-100 border-red-300' : result.metrics.riskSeverity > 40 ? 'bg-yellow-100 border-yellow-300' : 'bg-green-100 border-green-300'} border-2`}>
                <div className="flex items-center justify-between">
                    <div>
                        <h3 className="text-sm font-semibold text-slate-600 uppercase">Patient Condition</h3>
                        <p className={`text-3xl font-bold ${result.metrics.riskSeverity > 70 ? 'text-red-700' : result.metrics.riskSeverity > 40 ? 'text-yellow-700' : 'text-green-700'}`}>
                            {result.metrics.riskSeverity > 70 ? '🚨 SERIOUS' : result.metrics.riskSeverity > 40 ? '⚠️ MODERATE' : '✅ STABLE/OK'}
                        </p>
                    </div>
                    <div className="text-right">
                        <p className="text-sm text-slate-600">Risk Score</p>
                        <p className={`text-4xl font-bold ${result.metrics.riskSeverity > 70 ? 'text-red-600' : result.metrics.riskSeverity > 40 ? 'text-yellow-600' : 'text-green-600'}`}>
                            {result.metrics.riskSeverity.toFixed(0)}
                        </p>
                        <p className="text-xs text-slate-500">out of 100</p>
                    </div>
                </div>
            </div>

            {/* Narrative & Reasoning */}
            <div className="bg-white rounded-2xl p-8 shadow-sm border border-slate-100">
                <h3 className="text-lg font-bold text-slate-800 mb-4">🧠 Clinical Reasoning</h3>
                <div className="space-y-2">
                    {result.riskContext.map((ctx, i) => (
                        <div key={i} className={`p-3 rounded-lg ${ctx.includes("Normal") ? "bg-emerald-50 text-emerald-700" : "bg-amber-50 text-amber-700"}`}>
                            {ctx}
                        </div>
                    ))}
                    {(result.riskContext.length === 0) && <p className="text-slate-500">No specific risk factors identified.</p>}
                </div>
            </div>

            {/* Action Plan (Dos/Donts/Meds) */}
            {result.plan && (
                <div className="space-y-6">
                    {/* Dos and Donts */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="bg-emerald-50 p-6 rounded-2xl border border-emerald-100">
                            <h3 className="font-bold text-emerald-800 mb-4 flex items-center gap-2">✅ Do's / Advice</h3>
                            <ul className="space-y-2">
                                {result.plan.dos.map((item, i) => (
                                    <li key={i} className="flex items-center gap-2 text-emerald-700">
                                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" /></svg>
                                        {item}
                                    </li>
                                ))}
                            </ul>
                        </div>
                        <div className="bg-red-50 p-6 rounded-2xl border border-red-100">
                            <h3 className="font-bold text-red-800 mb-4 flex items-center gap-2">❌ Don'ts / Avoid</h3>
                            <ul className="space-y-2">
                                {result.plan.donts.map((item, i) => (
                                    <li key={i} className="flex items-center gap-2 text-red-700">
                                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" /></svg>
                                        {item}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>

                    {/* Prescriptions */}
                    <div className="bg-white rounded-2xl p-8 shadow-sm border border-emerald-100 relative overflow-hidden">
                        <div className="absolute top-0 right-0 p-4 opacity-10 text-emerald-600">
                            <svg className="w-32 h-32" fill="currentColor" viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-6 14h-2v-4h-4v-2h4V7h2v4h4v2h-4v4z" /></svg>
                        </div>

                        <h3 className="text-xl font-bold text-emerald-800 mb-6 flex items-center gap-2">
                            <span>💊</span> ePrescription & Meds
                        </h3>

                        <div className="space-y-4 relative z-10">
                            {result.plan.rx.map((rx, i) => (
                                <div key={i} className="bg-white border border-emerald-200 p-4 rounded-xl shadow-sm">
                                    <div className="flex justify-between items-start mb-2">
                                        <div className="flex-1">
                                            <p className="font-bold text-slate-800 text-lg">{rx.name}</p>
                                            <p className="text-slate-500">{rx.dose}</p>
                                            <p className="text-xs text-amber-600 mt-1 font-semibold uppercase">⚠️ {rx.warn}</p>
                                        </div>
                                        <div className="text-right">
                                            <span className="bg-emerald-100 text-emerald-700 text-xs px-2 py-1 rounded font-bold">DISPENSED</span>
                                        </div>
                                    </div>
                                    <div className="mt-3 pt-3 border-t border-slate-100">
                                        <p className="text-xs text-slate-500">📚 Source: <span className="text-blue-600 font-semibold">openFDA, NHS Guidelines</span></p>
                                    </div>
                                </div>
                            ))}
                        </div>

                        <div className="mt-6 pt-6 border-t border-slate-100">
                            <div className="bg-blue-50 p-4 rounded-lg mb-4">
                                <h4 className="font-bold text-blue-800 mb-2">🚚 Delivery Information</h4>
                                <p className="text-sm text-blue-700">Pharmacy: <strong>ExpressRx 24/7 Delivery</strong></p>
                                <p className="text-sm text-blue-700">Address: <strong>{result.address || "Please provide delivery address"}</strong></p>
                                <p className="text-sm text-blue-700">ETA: <strong>{result.plan.delivery.eta}</strong></p>
                                <p className="text-xs text-blue-500 mt-2">Track order: <a href="#" className="underline">Track #MED-{Math.floor(Math.random() * 10000)}</a></p>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            <button onClick={onReset} className="w-full py-4 text-slate-500 hover:text-slate-700 font-semibold">
                Start New Triage Case
            </button>
        </div>
    );
}

function MetricCard({ label, val }) {
    return (
        <div className="bg-white p-6 rounded-xl border border-slate-100 shadow-sm text-center">
            <h4 className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-2">{label}</h4>
            <p className="text-3xl font-extrabold text-slate-800">{val}</p>
        </div>
    );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
