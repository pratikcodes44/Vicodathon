import { DashboardClient } from "@/components/DashboardClient";
import { createClient } from "@/lib/supabase/server";

export const dynamic = "force-dynamic";

export default async function Home() {
  const supabase = await createClient();
  const { data: candidates, error } = await supabase
    .from("candidates")
    .select("*")
    .order("created_at", { ascending: true });

  if (error) {
    console.error("Error fetching candidates:", error);
  }

  return (
    <div className="max-w-[1920px] mx-auto min-h-screen p-8">
      <DashboardClient candidates={candidates || []} />
    </div>
  );
}
