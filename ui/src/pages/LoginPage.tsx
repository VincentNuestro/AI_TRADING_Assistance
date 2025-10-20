import { FormEvent, useState } from "react";
import axios from "axios";

interface LoginPageProps {
  onSuccess: () => void;
}

export function LoginPage({ onSuccess }: LoginPageProps) {
  const [email, setEmail] = useState("demo@local.test");
  const [password, setPassword] = useState("password123");
  const [error, setError] = useState<string | null>(null);
  const apiUrl = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    try {
      const response = await axios.post(
        `${apiUrl}/auth/login`,
        new URLSearchParams({ username: email, password })
      );
      if (response.data?.access_token) {
        onSuccess();
      }
    } catch (err) {
      setError("Invalid credentials");
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950 px-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm space-y-4 rounded-xl border border-slate-800 bg-slate-900/70 p-8 shadow-lg"
      >
        <div>
          <h1 className="text-xl font-semibold text-white">HullSuite Trader Login</h1>
          <p className="mt-1 text-sm text-slate-400">Enter your credentials to access the console.</p>
        </div>
        {error && <p className="rounded bg-red-500/20 px-3 py-2 text-sm text-red-200">{error}</p>}
        <label className="block text-sm">
          <span className="text-slate-300">Email</span>
          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="mt-1 w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100 focus:border-brand-500 focus:outline-none"
          />
        </label>
        <label className="block text-sm">
          <span className="text-slate-300">Password</span>
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="mt-1 w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100 focus:border-brand-500 focus:outline-none"
          />
        </label>
        <button
          type="submit"
          className="w-full rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-500"
        >
          Sign in
        </button>
      </form>
    </div>
  );
}
