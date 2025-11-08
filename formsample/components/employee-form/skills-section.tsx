"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

const SKILL_OPTIONS = [
  "S-OKR",
  "S-ANALISIS",
  "S-STAKE",
  "S-PM",
  "S-ANALYTICS",
  "S-CRM",
  "S-AUTOM",
  "S-DATA",
  "S-SQLPY",
  "S-EMAIL",
  "S-STORY",
  "S-COPY",
  "S-BRAND",
  "S-GENAI",
  "S-UIUX",
  "S-FIGMA",
  "S-ADS-GA",
  "S-ADS-META",
  "S-ABTEST",
  "S-SEO",
  "S-SOCIAL",
]

interface SkillsSectionProps {
  skills: Record<string, number>
  onChange: (skills: Record<string, number>) => void
}

export function SkillsSection({ skills, onChange }: SkillsSectionProps) {
  const [selectedSkill, setSelectedSkill] = useState("")
  const [skillRating, setSkillRating] = useState(5)

  const addSkill = () => {
    if (selectedSkill && !skills[selectedSkill]) {
      onChange({
        ...skills,
        [selectedSkill]: skillRating,
      })
      setSelectedSkill("")
      setSkillRating(5)
    }
  }

  const removeSkill = (skill: string) => {
    const { [skill]: _, ...remaining } = skills
    onChange(remaining)
  }

  return (
    <Card className="border-0 shadow-md">
      <CardHeader className="border-b bg-slate-50">
        <CardTitle className="text-primary">Habilidades</CardTitle>
        <CardDescription>Evalúa cada habilidad del 1 (mínimo) al 10 (máximo)</CardDescription>
      </CardHeader>
      <CardContent className="pt-6">
        <div className="space-y-6">
          {/* Add New Skill */}
          <div className="flex gap-3 pb-6 border-b">
            <select
              value={selectedSkill}
              onChange={(e) => setSelectedSkill(e.target.value)}
              className="flex-1 px-3 py-2 border border-input rounded-md bg-background text-foreground"
            >
              <option value="">Seleccionar habilidad...</option>
              {SKILL_OPTIONS.filter((skill) => !skills[skill]).map((skill) => (
                <option key={skill} value={skill}>
                  {skill}
                </option>
              ))}
            </select>
            <div className="flex items-center gap-2">
              <Input
                type="number"
                min="1"
                max="10"
                value={skillRating}
                onChange={(e) => setSkillRating(Math.min(10, Math.max(1, Number.parseInt(e.target.value) || 1)))}
                className="w-20"
              />
              <span className="text-xs text-muted-foreground">/10</span>
            </div>
            <Button onClick={addSkill} type="button" variant="default" className="px-6">
              Añadir
            </Button>
          </div>

          {/* Skills List */}
          {Object.keys(skills).length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(skills).map(([skill, rating]) => (
                <div key={skill} className="flex items-center justify-between p-4 bg-slate-50 rounded-lg border">
                  <div className="flex-1">
                    <p className="font-medium text-foreground">{skill}</p>
                    <div className="flex items-center gap-2 mt-2">
                      <div className="flex-1 h-2 bg-slate-200 rounded-full overflow-hidden">
                        <div className="h-full bg-primary" style={{ width: `${(rating / 10) * 100}%` }} />
                      </div>
                      <span className="text-sm font-semibold text-primary">{rating}/10</span>
                    </div>
                  </div>
                  <button
                    onClick={() => removeSkill(skill)}
                    className="ml-4 text-xs text-destructive hover:text-destructive/80"
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-center text-muted-foreground py-8">Añade habilidades para comenzar</p>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
