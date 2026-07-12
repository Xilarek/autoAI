import { HeroSection } from "@/components/home/HeroSection"
import { FeaturesGrid } from "@/components/home/FeaturesGrid"
import { AIIssuesGrid } from "@/components/home/AIIssuesGrid"
import { ComparisonCards } from "@/components/home/ComparisonCards"
import { CallToAction } from "@/components/home/CallToAction"

export default function HomePage() {
  return (
    <div className="space-y-8">
      <HeroSection />
      <FeaturesGrid />
      <AIIssuesGrid />
      <ComparisonCards />
      <CallToAction />
    </div>
  )
}
