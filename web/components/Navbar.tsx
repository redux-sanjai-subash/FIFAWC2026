"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import { useAuth } from "./AuthProvider";
import { Logout } from "./Icons";

const links = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/leaderboard", label: "Leaderboard" },
  { href: "/golden-boot", label: "Golden Boot" },
  { href: "/admin", label: "Admin" },
];

export default function Navbar() {
  const { user, logout } = useAuth();
  const pathname = usePathname();
  const router = useRouter();
  const [open, setOpen] = useState(false);

  const onLogout = async () => {
    await logout();
    router.push("/");
  };

  return (
    <header className="bg-transparent">
      <div className="container-lux flex h-16 items-center justify-between">
        <Link href={user ? "/dashboard" : "/"} className="flex items-center gap-3" aria-label="Home" />

        {user ? (
          <>
            <nav className="hidden items-center gap-7 md:flex">
              {links.map(({ href, label }) => {
                const active = pathname === href;
                return (
                  <Link
                    key={href}
                    href={href}
                    className={`relative text-sm transition ${
                      active ? "text-fg" : "text-muted hover:text-fg"
                    }`}
                  >
                    {label}
                    {active && <span className="absolute -bottom-[21px] left-0 h-px w-full bg-gold" />}
                  </Link>
                );
              })}
            </nav>

            <div className="hidden items-center gap-3 md:flex">
              <span className="flex items-center gap-2 text-sm text-muted">
                {user.favorite_team_flag && <span>{user.favorite_team_flag}</span>}
                {user.username}
              </span>
              <button onClick={onLogout} className="text-muted transition hover:text-gold" aria-label="Logout">
                <Logout width={18} height={18} />
              </button>
            </div>

            <div className="flex items-center gap-2 md:hidden">
              <button
                className="grid h-9 w-9 place-items-center rounded-lg border border-fg/12 text-fg"
                onClick={() => setOpen((v) => !v)}
                aria-label="Menu"
              >
                <div className="space-y-1.5">
                  <span className="block h-px w-5 bg-current" />
                  <span className="block h-px w-5 bg-current" />
                  <span className="block h-px w-5 bg-current" />
                </div>
              </button>
            </div>
          </>
        ) : null}
      </div>

      {user && open && (
        <div className="border-t border-fg/10 bg-transparent md:hidden">
          <nav className="container-lux flex flex-col py-2">
            {links.map(({ href, label }) => (
              <Link
                key={href}
                href={href}
                onClick={() => setOpen(false)}
                className={`border-b border-fg/5 py-3 text-sm ${
                  pathname === href ? "text-gold" : "text-muted"
                }`}
              >
                {label}
              </Link>
            ))}
            <button onClick={onLogout} className="py-3 text-left text-sm text-muted">
              Logout ({user.username})
            </button>
          </nav>
        </div>
      )}
    </header>
  );
}
