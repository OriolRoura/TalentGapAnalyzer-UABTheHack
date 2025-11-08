import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';

export function FutureVisionForm() {
  return (
    <Card className="border-0 shadow-md">
      <CardHeader className="border-b bg-slate-50">
        <CardTitle className="text-primary">Future Vision</CardTitle>
      </CardHeader>
      <CardContent className="pt-6">
        <p className="text-gray-600">Future Vision content here...</p>
      </CardContent>
    </Card>
  );
}
