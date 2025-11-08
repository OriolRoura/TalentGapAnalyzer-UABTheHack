"use client"

import type React from "react"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { SkillsSection } from "./employee-form/skills-section"
import { DedicationSection } from "./employee-form/dedication-section"
import { AmbitionsSection } from "./employee-form/ambitions-section"

const CHAPTERS = ["Strategy", "Martech", "Creative", "Design", "Performance", "Influency"]
const ROLES = [
  "Head of Strategy",
  "Project Manager",
  "Martech Architect",
  "CRM Admin",
  "Data Analyst",
  "Creative Director",
  "Senior Brand/UI Designer",
  "Performance Media Specialist",
  "SEO/SEM Manager",
  "Social Media Strategist",
]
const PERFORMANCE_RATINGS = ["D-", "D", "D+", "C-", "C", "C+", "B-", "B", "B+", "A-", "A", "A+"]
const RETENTION_RISKS = ["Baja", "Media", "Alta"]
const DEDICATION_PROJECTS = ["Royal", "Arquimbau", "Quether GTM", "Internal Ops", "I+D", "Events"]

interface FormData {
  nombre: string
  email: string
  chapter: string
  rol_actual: string
  manager: string
  antigüedad: string
  performance_rating: string
  retention_risk: string
  trayectoria: string
  habilidades: Record<string, number>
  dedicacion: Record<string, number>
  ambiciones: {
    nivel_aspiración: string
    especialidades_preferidas: string[]
  }
}

export function EmployeeForm() {
  const [formData, setFormData] = useState<FormData>({
    nombre: "",
    email: "",
    chapter: "",
    rol_actual: "",
    manager: "",
    antigüedad: "",
    performance_rating: "",
    retention_risk: "",
    trayectoria: "",
    habilidades: {},
    dedicacion: {},
    ambiciones: {
      nivel_aspiración: "",
      especialidades_preferidas: [],
    },
  })

  const [submitted, setSubmitted] = useState(false)

  const handleBasicChange = (field: string, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }))
  }

  const handleSkillsChange = (skills: Record<string, number>) => {
    setFormData((prev) => ({
      ...prev,
      habilidades: skills,
    }))
  }

  const handleDedicationChange = (dedication: Record<string, number>) => {
    setFormData((prev) => ({
      ...prev,
      dedicacion: dedication,
    }))
  }

  const handleAmbitionsChange = (ambiciones: { nivel_aspiración: string; especialidades_preferidas: string[] }) => {
    setFormData((prev) => ({
      ...prev,
      ambiciones,
    }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    console.log("Employee Data:", formData)
    setSubmitted(true)
    setTimeout(() => setSubmitted(false), 3000)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Basic Information */}
      <Card className="border-0 shadow-md">
        <CardHeader className="border-b bg-slate-50">
          <CardTitle className="text-primary">Información Básica</CardTitle>
          <CardDescription>Datos principales del empleado</CardDescription>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium mb-2 text-foreground">Nombre *</label>
              <Input
                type="text"
                placeholder="Nombre completo"
                value={formData.nombre}
                onChange={(e) => handleBasicChange("nombre", e.target.value)}
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2 text-foreground">Email *</label>
              <Input
                type="email"
                placeholder="email@empresa.com"
                value={formData.email}
                onChange={(e) => handleBasicChange("email", e.target.value)}
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2 text-foreground">Capítulo *</label>
              <Select value={formData.chapter} onValueChange={(value) => handleBasicChange("chapter", value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Seleccionar capítulo" />
                </SelectTrigger>
                <SelectContent>
                  {CHAPTERS.map((chapter) => (
                    <SelectItem key={chapter} value={chapter}>
                      {chapter}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2 text-foreground">Rol Actual *</label>
              <Select value={formData.rol_actual} onValueChange={(value) => handleBasicChange("rol_actual", value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Seleccionar rol" />
                </SelectTrigger>
                <SelectContent>
                  {ROLES.map((role) => (
                    <SelectItem key={role} value={role}>
                      {role}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2 text-foreground">Gerente/Superior</label>
              <Input
                type="text"
                placeholder="Nombre del superior directo"
                value={formData.manager}
                onChange={(e) => handleBasicChange("manager", e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2 text-foreground">Antigüedad (meses)</label>
              <Input
                type="number"
                placeholder="Ej: 12"
                value={formData.antigüedad}
                onChange={(e) => handleBasicChange("antigüedad", e.target.value)}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Performance & Risk */}
      <Card className="border-0 shadow-md">
        <CardHeader className="border-b bg-slate-50">
          <CardTitle className="text-primary">Desempeño y Retención</CardTitle>
          <CardDescription>Evaluación de rendimiento y riesgo de retención</CardDescription>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label className="block text-sm font-medium mb-2 text-foreground">Performance Rating</label>
              <Select
                value={formData.performance_rating}
                onValueChange={(value) => handleBasicChange("performance_rating", value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Seleccionar calificación" />
                </SelectTrigger>
                <SelectContent>
                  {PERFORMANCE_RATINGS.map((rating) => (
                    <SelectItem key={rating} value={rating}>
                      {rating}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2 text-foreground">Riesgo de Retención</label>
              <Select
                value={formData.retention_risk}
                onValueChange={(value) => handleBasicChange("retention_risk", value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Seleccionar riesgo" />
                </SelectTrigger>
                <SelectContent>
                  {RETENTION_RISKS.map((risk) => (
                    <SelectItem key={risk} value={risk}>
                      {risk}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2 text-foreground">Trayectoria</label>
              <Input
                type="text"
                placeholder="Ej: Junior > Mid (6m)"
                value={formData.trayectoria}
                onChange={(e) => handleBasicChange("trayectoria", e.target.value)}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Detailed Sections */}
      <Tabs defaultValue="skills" className="w-full">
        <TabsList className="grid w-full grid-cols-3 bg-slate-100">
          <TabsTrigger value="skills">Habilidades</TabsTrigger>
          <TabsTrigger value="dedication">Dedicación</TabsTrigger>
          <TabsTrigger value="ambitions">Ambiciones</TabsTrigger>
        </TabsList>

        <TabsContent value="skills" className="mt-6">
          <SkillsSection skills={formData.habilidades} onChange={handleSkillsChange} />
        </TabsContent>

        <TabsContent value="dedication" className="mt-6">
          <DedicationSection
            dedication={formData.dedicacion}
            onChange={handleDedicationChange}
            projects={DEDICATION_PROJECTS}
          />
        </TabsContent>

        <TabsContent value="ambitions" className="mt-6">
          <AmbitionsSection ambiciones={formData.ambiciones} onChange={handleAmbitionsChange} />
        </TabsContent>
      </Tabs>

      {/* Submit Button */}
      <div className="flex gap-4 justify-end pt-4">
        <Button type="button" variant="outline" className="px-8 bg-transparent">
          Cancelar
        </Button>
        <Button type="submit" className="px-8 bg-primary hover:bg-primary/90">
          {submitted ? "✓ Empleado Añadido" : "Guardar Empleado"}
        </Button>
      </div>
    </form>
  )
}
