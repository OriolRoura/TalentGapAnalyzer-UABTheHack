"use client"
import { EmployeeForm } from "@/components/employee-form"

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-background to-slate-50 py-8 px-4">
      <div className="max-w-5xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-foreground mb-2">Gestión de Empleados</h1>
          <p className="text-muted-foreground">
            Añade un nuevo empleado al sistema con todos sus detalles, habilidades y aspiraciones
          </p>
        </div>
        <EmployeeForm />
      </div>
    </main>
  )
}
