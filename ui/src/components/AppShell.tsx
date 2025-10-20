import { ReactNode } from "react";
import { Disclosure } from "@headlessui/react";
import { Bars3Icon, XMarkIcon } from "@heroicons/react/24/outline";
import { Link, Outlet, useLocation } from "react-router-dom";
import clsx from "clsx";

const navigation = [
  { name: "Dashboard", href: "/" },
  { name: "Predictions", href: "/predictions" },
  { name: "Monte Carlo", href: "/monte-carlo" },
  { name: "Risk", href: "/risk" },
  { name: "History", href: "/history" },
  { name: "Accounts", href: "/accounts" },
  { name: "Reports", href: "/reports" },
  { name: "Users", href: "/users" }
];

interface AppShellProps {
  onLogout: () => void;
  children?: ReactNode;
}

export function AppShell({ onLogout }: AppShellProps) {
  const location = useLocation();

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <Disclosure as="nav" className="border-b border-slate-800 bg-slate-900/80 backdrop-blur">
        {({ open }) => (
          <>
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
              <div className="flex h-16 items-center justify-between">
                <div className="flex items-center gap-4">
                  <span className="text-lg font-semibold text-brand-500">HullSuite Trader</span>
                  <div className="hidden md:block">
                    <div className="flex items-baseline space-x-4">
                      {navigation.map((item) => (
                        <Link
                          key={item.name}
                          to={item.href}
                          className={clsx(
                            "rounded-md px-3 py-2 text-sm font-medium transition",
                            location.pathname === item.href
                              ? "bg-brand-600 text-white"
                              : "text-slate-300 hover:bg-slate-800 hover:text-white"
                          )}
                        >
                          {item.name}
                        </Link>
                      ))}
                    </div>
                  </div>
                </div>
                <div className="hidden md:block">
                  <button
                    type="button"
                    onClick={onLogout}
                    className="rounded-md bg-slate-800 px-4 py-2 text-sm font-medium text-slate-100 hover:bg-slate-700"
                  >
                    Log out
                  </button>
                </div>
                <div className="-mr-2 flex md:hidden">
                  <Disclosure.Button className="inline-flex items-center justify-center rounded-md p-2 text-slate-200 hover:bg-slate-800 hover:text-white">
                    <span className="sr-only">Open main menu</span>
                    {open ? <XMarkIcon className="h-6 w-6" /> : <Bars3Icon className="h-6 w-6" />}
                  </Disclosure.Button>
                </div>
              </div>
            </div>

            <Disclosure.Panel className="border-t border-slate-800 md:hidden">
              <div className="space-y-1 px-2 pt-2 pb-3 sm:px-3">
                {navigation.map((item) => (
                  <Disclosure.Button
                    key={item.name}
                    as={Link}
                    to={item.href}
                    className={clsx(
                      "block rounded-md px-3 py-2 text-base font-medium",
                      location.pathname === item.href
                        ? "bg-brand-600 text-white"
                        : "text-slate-300 hover:bg-slate-800 hover:text-white"
                    )}
                  >
                    {item.name}
                  </Disclosure.Button>
                ))}
                <Disclosure.Button
                  as="button"
                  onClick={onLogout}
                  className="block w-full rounded-md bg-slate-800 px-3 py-2 text-left text-base font-medium text-slate-100 hover:bg-slate-700"
                >
                  Log out
                </Disclosure.Button>
              </div>
            </Disclosure.Panel>
          </>
        )}
      </Disclosure>
      <main className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        <Outlet />
      </main>
    </div>
  );
}
