import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import UserInfo from './UserInfo';
import { Link, NavLink } from 'react-router-dom';
import { Brain, Menu, Moon, Sun, X, MoreVertical, User as UserIcon } from 'lucide-react';

const navItems = [
  { name: 'Home', path: '/' },
  { name: 'Dashboard', path: '/dashboard' },
];

const Navbar = ({ theme = 'light', onToggleTheme }) => {
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const navigate = useNavigate();
  const isAuthenticated = Boolean(localStorage.getItem('access'));
  const handleLogout = () => {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    navigate('/login');
  };

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
          {/* Profile dropdown */}
          {isAuthenticated ? (
            <div className="relative">
              <button
                type="button"
                className="rounded-full p-2 text-muted-foreground hover:bg-muted/60 hover:text-foreground transition-colors border border-border"
                aria-label="Open profile menu"
                onClick={() => { setIsProfileOpen((v) => !v); setIsMenuOpen(false); }}
              >
                <UserIcon className="h-5 w-5" />
              </button>
              {isProfileOpen && (
                <div className="absolute right-0 mt-2 w-56 rounded-xl border border-border bg-gradient-to-br from-slate-100 via-slate-50 to-slate-200 dark:from-slate-800 dark:via-slate-700 dark:to-slate-900 shadow-lg z-50 flex flex-col p-2 backdrop-blur-sm">
                  <div className="px-3 py-2 border-b border-border mb-2">
                    <UserInfo />
                  </div>
                  <button
                    type="button"
                    onClick={() => { handleLogout(); setIsProfileOpen(false); }}
                    className="w-full text-left px-4 py-2 rounded-lg hover:bg-muted/60"
                  >Logout</button>
                </div>
              )}
            </div>
          ) : (
            <Link to="/login" className="btn-primary px-4 py-2">Login</Link>
          )}
          {/* 3-dot menu for theme toggle */}
          <div className="relative">
            <button
              type="button"
              className="rounded-lg p-2 text-muted-foreground hover:bg-muted/60 hover:text-foreground transition-colors"
              aria-label="Open menu"
              onClick={() => { setIsMenuOpen((v) => !v); setIsProfileOpen(false); }}
            >
              <MoreVertical className="h-5 w-5" />
            </button>
            {isMenuOpen && (
              <div className="absolute right-0 mt-2 w-40 rounded-xl border border-border bg-gradient-to-br from-slate-100 via-slate-50 to-slate-200 dark:from-slate-800 dark:via-slate-700 dark:to-slate-900 shadow-lg z-50 flex flex-col backdrop-blur-sm">
                <button
                  type="button"
                  onClick={() => { onToggleTheme(); setIsMenuOpen(false); }}
                  className="flex items-center gap-2 px-4 py-2 hover:bg-muted/60 rounded-t-xl"
                >
                  {isDark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
                  <span>Toggle Mode</span>
                </button>
              </div>
            )}
          </div>
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
            {isAuthenticated ? (
              <button onClick={() => { setIsMobileOpen(false); handleLogout(); }} className="mt-2 btn-primary px-4 py-2">Logout</button>
            ) : (
              <Link to="/login" onClick={() => setIsMobileOpen(false)} className="mt-2 btn-primary px-4 py-2">Login</Link>
            )}
          </nav>
        </div>
      )}
    </header>
  );
};

export default Navbar;