// EGOS Dashboard integration via iframe
import React from 'react';

export default function DashboardPage() {
  return (
    <main className="min-h-screen w-full flex flex-col items-center justify-center bg-background">
      <h1 className="text-2xl font-bold mb-4 text-foreground">EGOS Monitoring Dashboard</h1>
      <div className="w-full h-[80vh] max-w-6xl rounded-lg overflow-hidden shadow-lg border border-border bg-card">
        <iframe
          src="https://egosos.streamlit.app/"
          title="EGOS Dashboard"
          width="100%"
          height="100%"
          style={{ minHeight: '600px', border: 'none' }}
          allowFullScreen
        />
      </div>
      <p className="mt-4 text-sm text-muted-foreground">
        O dashboard é hospedado 24h na nuvem (Streamlit Cloud) e está sempre sincronizado com o repositório <a href="https://github.com/enioxt/egos" target="_blank" rel="noopener noreferrer" className="underline text-blue-600 hover:text-blue-800">EGOS no GitHub</a>.<br/>
        Se preferir, <a href="https://egosos.streamlit.app/" target="_blank" rel="noopener noreferrer" className="underline text-blue-600 hover:text-blue-800">abra o dashboard em nova aba</a>.
      </p>
    </main>
  );
}
