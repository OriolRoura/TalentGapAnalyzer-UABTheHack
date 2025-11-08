"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

const ASPIRATION_LEVELS = ["junior", "mid", "senior", "lead", "director", "executive"]
const SPECIALTIES = [
  "Estrategia",
  "Pricing",
  "GTM",
  "PMO",
  "Operations",
  "RevOps",
  "Automatización",
  "Community",
  "Content",
  "Brand Narrative",
  "Design Systems",
  "UI",
  "Paid Media",
  "Experimentación",
  "SEO Técnico",
  "Content SEO",
  "BI",
  "Atribución",
]

interface AmbitionsData {
  nivel_aspiración: string
  especialidades_preferidas: string[]
}

interface AmbitionsSectionProps {
  ambiciones: AmbitionsData
  onChange: (ambiciones: AmbitionsData) => void
}

export function AmbitionsSection({ ambiciones, onChange }: AmbitionsSectionProps) {
  const [selectedSpecialty, setSelectedSpecialty] = useState("")

  const addSpecialty = () => {
    if (selectedSpecialty && !ambiciones.especialidades_preferidas.includes(selectedSpecialty)) {
      onChange({
        ...ambiciones,
        especialidades_preferidas: [...ambiciones.especialidades_preferidas, selectedSpecialty],
      })
      setSelectedSpecialty("")
    }
  }

  const removeSpecialty = (specialty: string) => {
    onChange({
      ...ambiciones,
      especialidades_preferidas: ambiciones.especialidades_preferidas.filter((s) => s !== specialty),
    })
  }

  return (
    <Card className="border-0 shadow-md">
      <CardHeader className="border-b bg-slate-50">
        <CardTitle className="text-primary">Ambiciones Profesionales</CardTitle>
        <CardDescription>Define el nivel de aspiración y especialidades preferidas</CardDescription>
      </CardHeader>
      <CardContent className="pt-6">
        <div className="space-y-6">
          {/* Aspiration Level */}
          <div>
            <label className="block text-sm font-medium mb-2 text-foreground">Nivel de Aspiración</label>
            <Select
              value={ambiciones.nivel_aspiración}
              onValueChange={(value) =>
                onChange({
                  ...ambiciones,
                  nivel_aspiración: value,
                })
              }
            >
              <SelectTrigger>
                <SelectValue placeholder="Seleccionar nivel" />
              </SelectTrigger>
              <SelectContent>
                {ASPIRATION_LEVELS.map((level) => (
                  <SelectItem key={level} value={level}>
                    {level.charAt(0).toUpperCase() + level.slice(1)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Specialties */}
          <div>
            <label className="block text-sm font-medium mb-2 text-foreground">Especialidades Preferidas</label>
            <div className="flex gap-2 mb-4">
              <select
                value={selectedSpecialty}
                onChange={(e) => setSelectedSpecialty(e.target.value)}
                className="flex-1 px-3 py-2 border border-input rounded-md bg-background text-foreground"
              >
                <option value="">Seleccionar especialidad...</option>
                {SPECIALTIES.filter((spec) => !ambiciones.especialidades_preferidas.includes(spec)).map((spec) => (
                  <option key={spec} value={spec}>
                    {spec}
                  </option>
                ))}
              </select>
              <Button onClick={addSpecialty} type="button" variant="default">
                Añadir
              </Button>
            </div>

            {/* Specialties Tags */}
            {ambiciones.especialidades_preferidas.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {ambiciones.especialidades_preferidas.map((specialty) => (
                  <div
                    key={specialty}
                    className="inline-flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-full text-sm"
                  >
                    {specialty}
                    <button onClick={() => removeSpecialty(specialty)} className="hover:opacity-70" type="button">
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-center text-muted-foreground py-8">No hay especialidades seleccionadas</p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
