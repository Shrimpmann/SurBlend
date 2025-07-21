import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { useForm, Controller } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { toast } from '@/components/ui/use-toast';
import { chemicalsApi } from '@/services/api';

const chemicalSchema = z.object({
  name: z.string().min(1, 'Chemical name is required'),
  aiPercentage: z.number().min(0, 'AI percentage must be non-negative').max(100, 'AI percentage cannot exceed 100%'),
  costPerUnit: z.number().min(0, 'Cost must be non-negative'),
  displayOrder: z.number().min(0, 'Display order must be non-negative'),
});

type ChemicalForm = z.infer<typeof chemicalSchema>;
type Chemical = {
  id: number;
  name: string;
  aiPercentage: number;
  costPerUnit: number;
  displayOrder: number;
};

function Chemicals() {
  const [chemicals, setChemicals] = useState<Chemical[]>([]);
  const { control, handleSubmit, reset, formState: { errors } } = useForm<ChemicalForm>({
    resolver: zodResolver(chemicalSchema),
    defaultValues: { name: '', aiPercentage: 0, costPerUnit: 0, displayOrder: 0 },
  });

  useEffect(() => {
    const fetchChemicals = async () => {
      try {
        const response = await chemicalsApi.getAll();
        setChemicals(response.data.sort((a: Chemical, b: Chemical) => a.displayOrder - b.displayOrder));
      } catch (error) {
        toast({ variant: 'destructive', title: 'Error', description: 'Failed to fetch chemicals' });
      }
    };
    fetchChemicals();
  }, []);

  const onSubmit = async (data: ChemicalForm) => {
    try {
      await chemicalsApi.create(data);
      const response = await chemicalsApi.getAll();
      setChemicals(response.data.sort((a: Chemical, b: Chemical) => a.displayOrder - b.displayOrder));
      reset();
      toast({ title: 'Success', description: 'Chemical added successfully' });
    } catch (error) {
      toast({ variant: 'destructive', title: 'Error', description: 'Failed to add chemical' });
    }
  };

  const deleteChemical = async (id: number) => {
    try {
      await chemicalsApi.delete(id);
      setChemicals(chemicals.filter(chem => chem.id !== id));
      toast({ title: 'Success', description: 'Chemical deleted successfully' });
    } catch (error) {
      toast({ variant: 'destructive', title: 'Error', description: 'Failed to delete chemical' });
    }
  };

  return (
    <div className="container mx-auto p-6">
      <Card className="max-w-4xl mx-auto">
        <CardHeader>
          <CardTitle className="text-2xl text-green-700">Chemicals Management</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 mb-6">
            <div>
              <Label htmlFor="name">Chemical Name</Label>
              <Controller
                name="name"
                control={control}
                render={({ field }) => <Input {...field} className="mt-1" />}
              />
              {errors.name && <p className="text-red-600 text-sm">{errors.name.message}</p>}
            </div>
            <div>
              <Label htmlFor="aiPercentage">AI Percentage (%)</Label>
              <Controller
                name="aiPercentage"
                control={control}
                render={({ field }) => (
                  <Input
                    type="number"
                    {...field}
                    onChange={e => field.onChange(parseFloat(e.target.value))}
                    className="mt-1"
                  />
                )}
              />
              {errors.aiPercentage && <p className="text-red-600 text-sm">{errors.aiPercentage.message}</p>}
            </div>
            <div>
              <Label htmlFor="costPerUnit">Cost per Unit ($)</Label>
              <Controller
                name="costPerUnit"
                control={control}
                render={({ field }) => (
                  <Input
                    type="number"
                    {...field}
                    onChange={e => field.onChange(parseFloat(e.target.value))}
                    className="mt-1"
                  />
                )}
              />
              {errors.costPerUnit && <p className="text-red-600 text-sm">{errors.costPerUnit.message}</p>}
            </div>
            <div>
              <Label htmlFor="displayOrder">Display Order</Label>
              <Controller
                name="displayOrder"
                control={control}
                render={({ field }) => (
                  <Input
                    type="number"
                    {...field}
                    onChange={e => field.onChange(parseInt(e.target.value))}
                    className="mt-1"
                  />
                )}
              />
              {errors.displayOrder && <p className="text-red-600 text-sm">{errors.displayOrder.message}</p>}
            </div>
            <Button type="submit" className="w-full bg-green-600 hover:bg-green-700 text-white">
              Add Chemical
            </Button>
          </form>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>AI Percentage (%)</TableHead>
                <TableHead>Cost ($/unit)</TableHead>
                <TableHead>Display Order</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {chemicals.map(chem => (
                <TableRow key={chem.id}>
                  <TableCell>{chem.name}</TableCell>
                  <TableCell>{chem.aiPercentage.toFixed(2)}</TableCell>
                  <TableCell>${chem.costPerUnit.toFixed(2)}</TableCell>
                  <TableCell>{chem.displayOrder}</TableCell>
                  <TableCell>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => deleteChemical(chem.id)}
                    >
                      Delete
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}

export default Chemicals;
