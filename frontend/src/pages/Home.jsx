import { Link } from 'react-router-dom';
import { Brain, Activity, Microscope, Shield, ArrowRight } from 'lucide-react';
import HeroSlider from '../components/HeroSlider';

function Home() {
  const featureCards = [
    {
      title: 'Stroke Detection',
      description: 'Advanced analysis for rapid ischemic and hemorrhagic stroke identification.',
      icon: Activity,
      accent: 'primary',
      bullets: ['Ischemic & hemorrhagic detection', 'Real-time analysis results', '94.5% clinical accuracy'],
    },
    {
      title: 'Tumor Detection',
      description: 'Precise classification with segmentation insights for treatment planning.',
      icon: Microscope,
      accent: 'secondary',
      bullets: ['Multi-class tumor insights', 'Size & location mapping', '92.8% detection accuracy'],
    },
    {
      title: "Alzheimer's Detection",
      description: 'Early-stage cognitive decline detection powered by volumetric evaluation.',
      icon: Brain,
      accent: 'accent',
      bullets: ['Stage classification', 'Hippocampal atrophy focus', '91.2% prediction accuracy'],
    },
  ];

  const accentStyles = {
    primary: {
      cardBorder: 'border-border/40 hover:border-slate-300 dark:hover:border-slate-500',
      iconBg: 'bg-primary/10',
      iconColor: 'text-primary',
    },
    secondary: {
      cardBorder: 'border-border/40 hover:border-slate-300 dark:hover:border-slate-500',
      iconBg: 'bg-secondary/10',
      iconColor: 'text-secondary',
    },
    accent: {
      cardBorder: 'border-border/40 hover:border-slate-300 dark:hover:border-slate-500',
      iconBg: 'bg-accent/10',
      iconColor: 'text-accent',
    },
  };

  const benefits = [
    {
      title: 'Clinical Grade Security',
      description: 'HIPAA-compliant processing with end-to-end encryption for patient data.',
      icon: Shield,
    },
    {
      title: 'Rapid Analysis',
      description: 'Obtain results in seconds thanks to optimized inference pipelines.',
      icon: Activity,
    },
    {
      title: 'Research Backed',
      description: 'Built on peer-reviewed research and validated on thousands of studies.',
      icon: Microscope,
    },
    {
      title: 'Comprehensive Dashboard',
      description: 'Monitor histories, compare sessions, and export clinician-ready summaries.',
      icon: Brain,
    },
  ];

  return (
    <div className="min-h-screen bg-background text-foreground">
      <section className="px-6 pt-10">
        <HeroSlider>
          <div className="flex flex-col items-center gap-5 text-white">
            <div className="inline-flex items-center gap-3 rounded-full bg-white/10 px-5 py-2 text-sm font-semibold tracking-wide shadow-lg">
              <Brain className="h-5 w-5" />
              Clinical AI for brain health
            </div>
            <h1 className="text-4xl md:text-6xl font-bold leading-tight max-w-4xl">
              Advanced brain disease detection, now with a live RAG assistant
            </h1>
            <div className="flex flex-wrap justify-center gap-3">
              <Link to="/dashboard" className="btn-primary px-6 py-3 text-base shadow-lg">
                Start analyzing
                <ArrowRight className="h-5 w-5" />
              </Link>
              <Link to="/dashboard" className="px-6 py-3 text-base font-semibold rounded-full bg-white/20 backdrop-blur-sm text-white border-2 border-white/50 hover:bg-white/30 hover:border-white transition-all shadow-lg">
                Open Neuro Chat
              </Link>
            </div>
          </div>
        </HeroSlider>
      </section>

      <section className="px-6 py-20">
        <div className="mx-auto max-w-6xl text-center">
          <h2 className="text-3xl font-semibold md:text-4xl">
            Our detection capabilities
          </h2>
          <p className="mt-4 text-muted-foreground">
            Powered by proprietary datasets, medical experts, and continuous validation.
          </p>
        </div>
        <div className="mx-auto mt-12 grid max-w-6xl gap-8 md:grid-cols-3">
          {featureCards.map(({ title, description, icon: Icon, accent, bullets }) => {
            const { cardBorder, iconBg, iconColor } = accentStyles[accent] || accentStyles.primary;
            return (
              <div
                key={title}
                className={`card-gradient rounded-3xl border p-8 shadow-lg transition-all ${cardBorder}`}
              >
                <div className={`mb-6 w-fit rounded-2xl p-4 ${iconBg}`}>
                  <Icon className={`h-10 w-10 ${iconColor}`} />
                </div>
                <h3 className="text-xl font-semibold">{title}</h3>
                <p className="mt-3 text-sm text-muted-foreground">{description}</p>
                <ul className="mt-6 space-y-2 text-sm text-muted-foreground">
                  {bullets.map((line) => (
                    <li key={line} className="flex items-start gap-2">
                      <span className="text-primary">•</span>
                      <span>{line}</span>
                    </li>
                  ))}
                </ul>
              </div>
            );
          })}
        </div>
      </section>

      <section className="relative overflow-hidden bg-muted/60 px-6 py-20">
        <div className="absolute right-0 top-0 h-80 w-80 rounded-full bg-primary/5 blur-3xl" aria-hidden="true"></div>
        <div className="relative mx-auto max-w-6xl">
          <h2 className="text-center text-3xl font-semibold md:text-4xl">Why clinicians choose our system</h2>
          <div className="mt-12 grid gap-8 md:grid-cols-2">
            {benefits.map(({ title, description, icon: Icon }) => (
              <div key={title} className="flex gap-4 rounded-2xl border border-border/60 bg-card/60 p-6 shadow-sm">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
                  <Icon className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold">{title}</h3>
                  <p className="mt-2 text-sm text-muted-foreground">{description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <footer className="border-t border-border bg-card/60 px-6 py-10 text-sm text-muted-foreground">
        <div className="mx-auto flex max-w-6xl flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div className="text-left">
            <p className="text-base font-semibold text-foreground">NeuroScan AI</p>
            <p>Clinical AI for stroke, tumor, and Alzheimer’s screening.</p>
          </div>
          <div className="flex flex-wrap gap-3 text-xs md:gap-4">
            <span className="rounded-full bg-primary/10 px-3 py-1 text-primary font-semibold">HIPAA-aware workflows</span>
            <span className="rounded-full bg-secondary/10 px-3 py-1 text-secondary-foreground font-semibold">Secure uploads</span>
            <span className="rounded-full bg-accent/10 px-3 py-1 text-accent-foreground font-semibold">Fast inference</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default Home;