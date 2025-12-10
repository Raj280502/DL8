import { useState } from 'react';
import { Link, NavLink } from 'react-router-dom';
import { Brain, Menu, Moon, Sun, X } from 'lucide-react';

const navItems = [
  { name: 'Home', path: '/' },
  { name: 'Dashboard', path: '/dashboard' },
];

const Navbar = ({ theme = 'light', onToggleTheme }) => {
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  const isDark = theme === 'dark';

  const renderNavLink = (item, compact = false) => (
    <NavLink
      key={item.path}
      to={item.path}
      onClick={() => setIsMobileOpen(false)}
      className={({ isActive }) =>
        `flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-all ${
          isActive
            ? 'bg-primary/10 text-primary'
            : 'text-muted-foreground hover:bg-muted/60 hover:text-foreground'
        } ${compact ? 'justify-center' : ''}`
      }
    >
      {item.name}
    </NavLink>
  );

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-card/80 backdrop-blur">
      <div className="container mx-auto flex h-20 min-h-[4.5rem] items-center justify-between px-6">
        <Link to="/" className="flex items-center gap-3">
          <span className="medical-gradient rounded-lg p-2 shadow-xl glow-primary">
            <Brain className="h-6 w-6 text-primary-foreground" />
          </span>
          <div className="text-left">
            <p className="text-base font-semibold leading-tight">NeuroScan AI</p>
            <p className="text-xs text-muted-foreground">Precision brain analysis</p>
          </div>
        </Link>

        <nav className="hidden items-center gap-3 md:flex">
          {navItems.map((item) => renderNavLink(item))}
        </nav>

        <div className="hidden items-center gap-3 md:flex">
          <button
            type="button"
            onClick={onToggleTheme}
            className="rounded-lg p-2 text-muted-foreground hover:bg-muted/60 hover:text-foreground transition-colors"
            aria-label="Toggle color theme"
          >
            {isDark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
          </button>
          <Link
            to="/dashboard"
            className="btn-primary px-4 py-2"
          >
            Access Dashboard
          </Link>
        </div>

        <button
          type="button"
          className="rounded-md p-2 text-muted-foreground transition-colors hover:text-foreground md:hidden"
          onClick={() => setIsMobileOpen((prev) => !prev)}
          aria-label="Toggle navigation menu"
        >
          {isMobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {isMobileOpen && (
        <div className="border-t border-border bg-background px-6 py-4 md:hidden">
          <nav className="flex flex-col gap-2">
            {navItems.map((item) => renderNavLink(item, true))}
            <div className="flex justify-center">
              <button
                type="button"
                onClick={() => {
                  onToggleTheme?.();
                }}
                className="rounded-lg p-2 text-muted-foreground hover:bg-muted/60 hover:text-foreground transition-colors"
                aria-label="Toggle color theme"
              >
                {isDark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
              </button>
            </div>
            <Link
              to="/dashboard"
              onClick={() => setIsMobileOpen(false)}
              className="mt-2 btn-primary px-4 py-2"
            >
              Access Dashboard
            </Link>
          </nav>
        </div>
      )}
    </header>
  );
};

export default Navbar;