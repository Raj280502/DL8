import { Link } from 'react-router-dom';
import { Brain, Activity, Microscope, Shield, ArrowRight } from 'lucide-react';

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
      cardBorder: 'border-primary/30 hover:border-primary hover:glow-primary',
      iconBg: 'bg-primary/10',
      iconColor: 'text-primary',
    },
    secondary: {
      cardBorder: 'border-secondary/30 hover:border-secondary hover:glow-primary',
      iconBg: 'bg-secondary/10',
      iconColor: 'text-secondary',
    },
    accent: {
      cardBorder: 'border-accent/30 hover:border-accent hover:glow-accent',
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
      <section className="relative overflow-hidden px-6 py-24 text-center">
        <div className="absolute inset-0 hero-gradient" aria-hidden="true"></div>
        <div className="absolute inset-0 opacity-20" aria-hidden="true">
          <div className="absolute left-8 top-16 h-64 w-64 rounded-full bg-primary/30 blur-3xl animate-pulse-slow"></div>
          <div
            className="absolute bottom-16 right-10 h-72 w-72 rounded-full bg-accent/20 blur-3xl animate-pulse-slow"
            style={{ animationDelay: '1s' }}
          ></div>
        </div>
        <div className="relative mx-auto max-w-5xl">
          <div className="medical-gradient mx-auto mb-10 inline-flex items-center gap-4 rounded-2xl p-5 shadow-xl glow-primary animate-float">
            <Brain className="h-12 w-12 text-primary-foreground" />
            <span className="text-lg font-semibold text-primary-foreground">Clinical AI for Brain Health</span>
          </div>
          <h1 className="mb-6 text-5xl font-bold leading-tight md:text-6xl">
            Advanced Brain Disease Detection,
            <br className="hidden md:block" /> tailored for medical teams.
          </h1>
          <p className="mx-auto mb-10 max-w-3xl text-lg text-muted-foreground md:text-xl">
            Harness our YOLO-powered diagnostics for early detection of stroke, brain tumors, and Alzheimer&apos;s disease.
            Deliver timely insights with clinician-grade accuracy.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link
              to="/dashboard"
              className="inline-flex items-center gap-2 rounded-full bg-primary px-8 py-3 text-lg font-semibold text-primary-foreground shadow-lg transition-transform hover:scale-105 hover:glow-primary"
            >
              Launch Dashboard
              <ArrowRight className="h-5 w-5" />
            </Link>
            <Link
              to="/dashboard"
              className="inline-flex items-center gap-2 rounded-full border border-border px-8 py-3 text-lg font-semibold text-foreground transition-colors hover:bg-muted/70"
            >
              Explore Features
            </Link>
          </div>
        </div>
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
                <div className={`mb-6 w-fit rounded-2xl p-4 transition-all ${iconBg}`}>
                  <Icon className={`h-10 w-10 ${iconColor}`} />
                </div>
                <h3 className="text-xl font-semibold">{title}</h3>
                <p className="mt-3 text-sm text-muted-foreground">{description}</p>
                <ul className="mt-6 space-y-2 text-sm text-muted-foreground/90">
                  {bullets.map((line) => (
                    <li key={line}>• {line}</li>
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

      <section className="px-6 py-20 text-center">
        <div className="mx-auto max-w-3xl">
          <h2 className="text-3xl font-semibold md:text-4xl">Ready to accelerate diagnosis?</h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Join healthcare professionals using our AI-powered detection suite for better patient outcomes.
          </p>
          <Link
            to="/dashboard"
            className="mt-8 inline-flex items-center gap-2 rounded-full bg-primary px-8 py-3 text-lg font-semibold text-primary-foreground shadow-lg transition-transform hover:scale-105 hover:glow-primary"
          >
            Start analyzing now
            <ArrowRight className="h-5 w-5" />
          </Link>
        </div>
      </section>
    </div>
  );
}

export default Home;