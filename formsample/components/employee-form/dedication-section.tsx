"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"

interface DedicationSectionProps {
  dedication: Record<string, number>
  onChange: (dedication: Record<string, number>) => void
  projects: string[]
}

export function DedicationSection({ dedication, onChange, projects }: DedicationSectionProps) {
  const handleProjectChange = (project: string, value: string) => {
    const numValue = Math.min(100, Math.max(0, Number.parseInt(value) || 0))
    onChange({
      ...dedication,
      [project]: numValue,
    })
  }

  const totalDedication = Object.values(dedication).reduce((sum, val) => sum + val, 0)

  return (
    <Card className="border-0 shadow-md">
      <CardHeader className="border-b bg-slate-50">
        <CardTitle className="text-primary">Dedicación Actual</CardTitle>
        <CardDescription>Porcentaje de tiempo dedicado a cada proyecto</CardDescription>
      </CardHeader>
      <CardContent className="pt-6">
        <div className="space-y-6">
          {projects.map((project) => (
            <div key={project} className="space-y-2">
              <div className="flex justify-between items-center">
                <label className="text-sm font-medium text-foreground">{project}</label>
                <div className="flex items-center gap-2">
                  <Input
                    type="number"
                    min="0"
                    max="100"
                    value={dedication[project] || 0}
                    onChange={(e) => handleProjectChange(project, e.target.value)}
                    className="w-20"
                  />
                  <span className="text-xs text-muted-foreground">%</span>
                </div>
              </div>
              <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                <div className="h-full bg-primary transition-all" style={{ width: `${dedication[project] || 0}%` }} />
              </div>
            </div>
          ))}

          <div className="pt-4 border-t">
            <div className="flex justify-between items-center p-3 bg-slate-50 rounded-lg">
              <span className="font-medium text-foreground">Total Dedicación</span>
              <span
                className={`text-lg font-bold ${totalDedication === 100 ? "text-primary" : totalDedication > 100 ? "text-destructive" : "text-yellow-600"}`}
              >
                {totalDedication}%
              </span>
            </div>
            {totalDedication !== 100 && (
              <p className="text-xs text-muted-foreground mt-2">
                {totalDedication > 100 ? `Exceso de ${totalDedication - 100}%` : `Falta ${100 - totalDedication}%`}
              </p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
