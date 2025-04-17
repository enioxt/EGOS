// Import components
import { Header } from '@/components/Header';
import { Hero } from '@/components/Hero';
import { Principles } from '@/components/Principles';
import { Subsystems } from '@/components/Subsystems';
import { Roadmap } from '@/components/Roadmap';
import { CallToAction } from '@/components/CallToAction';
import { Footer } from '@/components/Footer';

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="flex-grow">
        <Hero />
        <Principles />
        <Subsystems />
        <Roadmap />
        <CallToAction />
      </main>
      <Footer />
    </div>
  );
}
