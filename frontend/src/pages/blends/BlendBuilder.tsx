import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { useForm, Controller } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { toast } from '@/components/ui/use-toast';
import { ingredientsApi, chemicalsApi, blendsApi } from '@/services/api';
import * as Solver from 'javascript-lp-solver';

const blendSchema = z.object({
  name: z.string().min(1, 'Blend name is required'),
  targetN: z.number().min(0, 'Nitrogen must be non-negative').max(100, 'Nitrogen cannot exceed 100%'),
  targetP: z.number().min(0, 'Phosphorus must be non-negative').max(100, 'Phosphorus cannot exceed 100%'),
  targetK: z.number().min(0, 'Potassium must be non-negative').max(100, 'Potassium cannot exceed 100%'),
  targetS: z.number().min(0, 'Sulfur must be non-negative').max(100, 'Sulfur cannot exceed 100%'),
  targetCa: z.number().min(0, 'Calcium must be non-negative').max(100, 'Calcium cannot exceed 100%'),
  targetMg: z.number().min(0, 'Magnesium must be non-negative').max(100, 'Magnesium cannot exceed 100%'),
  targetFe: z.number().min(0, 'Iron must be non-negative').max(100, 'Iron cannot exceed 100%'),
  targetZn: z.number().min(0, 'Zinc must be non-negative').max(100, 'Zinc cannot exceed 100%'),
  targetMn: z.number().min(0, 'Manganese must be non-negative').max(100, 'Manganese cannot exceed 100%'),
  targetB: z.number().min(0, 'Boron must be non-negative').max(100, 'Boron cannot exceed 100%'),
  targetCl: z.number().min(0, 'Chlorine must be non-negative').max(100, 'Chlorine cannot exceed 100%'),
  applicationRate: z.number().min(1, 'Application rate must be at least 1 lb/acre'),
  selectedIngredients: z.array(z.number()).min(1, 'Select at least one ingredient or chemical'),
  selectedChemicals: z.array(z.number()),
  chemicalQuantities: z.array(
    z.object({
      chemicalId: z.number(),
      aiPercentage: z.number().min(0, 'AI percentage must be non-negative').max(100, 'AI percentage cannot exceed 100%'),
    })
  ),
});

type BlendForm = z.infer<typeof blendSchema>;
type Ingredient = {
  id: number;
  name: string;
  n: number;
  p: number;
  k: number;
  s: number;
  ca: number;
  mg: number;
  fe: number;
  zn: number;
  mn: number;
  b: number;
  cl: number;
  costPerTon: number;
  displayOrder: number;
};
type Chemical = {
  id: number;
  name: string;
  aiPercentage: number;
  costPerUnit: number;
  displayOrder: number;
};
type BlendResult = { [key: string]: number; cost: number };

function BlendBuilder() {
  const navigate = useNavigate();
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [chemicals, setChemicals] = useState<Chemical[]>([]);
  const [blendResult, setBlendResult] = useState<BlendResult | null>(null);
  const { control, handleSubmit, formState: { errors }, watch, setValue } = useForm<BlendForm>({
    resolver: zodResolver(blendSchema),
    defaultValues: {
      name: '',
      targetN: 0,
      targetP: 0,
      targetK: 0,
      targetS: 0,
      targetCa: 0,
      targetMg: 0,
      targetFe: 0,
      targetZn: 0,
      targetMn: 0,
      targetB: 0,
      targetCl: 0,
      applicationRate: 100,
      selectedIngredients: [],
      selectedChemicals: [],
      chemicalQuantities: [],
    },
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [ingResponse, chemResponse] = await Promise.all([
          ingredientsApi.getAll(),
          chemicalsApi.getAll(),
        ]);
        setIngredients(ingResponse.data.sort((a: Ingredient, b: Ingredient) => a.displayOrder - b.displayOrder));
        setChemicals(chemResponse.data.sort((a: Chemical, b: Chemical) => a.displayOrder - b.displayOrder));
      } catch (error) {
        toast({ variant: 'destructive', title: 'Error', description: 'Failed to fetch data' });
      }
    };
    fetchData();
  }, []);

  const selectedChemicals = watch('selectedChemicals');
  useEffect(() => {
    const newQuantities = selectedChemicals.map(id => ({
      chemicalId: id,
      aiPercentage: 0,
    }));
    setValue('chemicalQuantities', newQuantities);
  }, [selectedChemicals, setValue]);

  const optimizeBlend = (data: BlendForm) => {
    const { targetN, targetP, targetK, targetS, targetCa, targetMg, targetFe, targetZn, targetMn, targetB, targetCl, applicationRate } = data;
    const model = {
      optimize: 'cost',
      opType: 'min',
      constraints: {
        n: { equal: targetN * applicationRate / 100 },
        p: { equal: targetP * applicationRate / 100 },
        k: { equal: targetK * applicationRate / 100 },
        s: { equal: targetS * applicationRate / 100 },
        ca: { equal: targetCa * applicationRate / 100 },
        mg: { equal: targetMg * applicationRate / 100 },
        fe: { equal: targetFe * applicationRate / 100 },
        zn: { equal: targetZn * applicationRate / 100 },
        mn: { equal: targetMn * applicationRate / 100 },
        b: { equal: targetB * applicationRate / 100 },
        cl: { equal: targetCl * applicationRate / 100 },
      },
      variables: {},
      ids: {},
    };

    ingredients
      .filter(ing => data.selectedIngredients.includes(ing.id))
      .forEach((ing, index) => {
        model.variables[`ing_${ing.name}`] = {
          n: ing.n * applicationRate / 100,
          p: ing.p * applicationRate / 100,
          k: ing.k * applicationRate / 100,
          s: ing.s * applicationRate / 100,
          ca: ing.ca * applicationRate / 100,
          mg: ing.mg * applicationRate / 100,
          fe: ing.fe * applicationRate / 100,
          zn: ing.zn * applicationRate / 100,
          mn: ing.mn * applicationRate / 100,
          b: ing.b * applicationRate / 100,
          cl: ing.cl * applicationRate / 100,
          cost: ing.costPerTon,
          [`ing_${ing.name}`]: 1,
        };
        model.ids[`ing_${ing.name}`] = index;
      });

    chemicals
      .filter(chem => data.selectedChemicals.includes(chem.id))
      .forEach((chem, index) => {
        const quantity = data.chemicalQuantities.find(q => q.chemicalId === chem.id)?.aiPercentage || 0;
        if (quantity > 0) {
          model.variables[`chem_${chem.name}`] = {
            ai: quantity * applicationRate / 100,
            cost: chem.costPerUnit * (quantity / chem.aiPercentage),
            [`chem_${chem.name}`]: 1,
          };
          model.ids[`chem_${chem.name}`] = index + ingredients.length;
        }
      });

    const result = Solver.Solve(model);
    if (result.feasible) {
      setBlendResult({ ...result, cost: result.result });
    } else {
      toast({ variant: 'destructive', title: 'Error', description: 'No feasible blend found' });
    }
  };

  const saveBlend = async (data: BlendForm) => {
    if (!blendResult) return;
    try {
      const blendData = {
        name: data.name,
        ingredients: Object.entries(blendResult)
          .filter(([key]) => key.startsWith('ing_') && key !== 'cost' && key !== 'feasible' && key !== 'result')
          .map(([key, quantity]) => ({
            ingredientId: ingredients.find(ing => `ing_${ing.name}` === key)?.id,
            quantity,
          })),
        chemicals: Object.entries(blendResult)
          .filter(([key]) => key.startsWith('chem_') && key !== 'cost' && key !== 'feasible' && key !== 'result')
          .map(([key, quantity]) => ({
            chemicalId: chemicals.find(chem => `chem_${chem.name}` === key)?.id,
            aiPercentage: data.chemicalQuantities.find(q => q.chemicalId === chemicals.find(chem => `chem_${chem.name}` === key)?.id)?.aiPercentage || 0,
          })),
        totalCost: blendResult.cost,
        applicationRate: data.applicationRate,
        nutrients: {
          n: data.targetN,
          p: data.targetP,
          k: data.targetK,
          s: data.targetS,
          ca: data.targetCa,
          mg: data.targetMg,
          fe: data.targetFe,
          zn: data.targetZn,
          mn: data.targetMn,
          b: data.targetB,
          cl: data.targetCl,
        },
      };
      await blendsApi.create(blendData);
      toast({ title: 'Success', description: 'Blend saved successfully' });
      navigate('/blends');
    } catch (error) {
      toast({ variant: 'destructive', title: 'Error', description: 'Failed to save blend' });
    }
  };

  const onSubmit = (data: BlendForm) => {
    optimizeBlend(data);
    saveBlend(data);
  };

  return (
    <div className="container mx-auto p-6">
      <Card className="max-w-4xl mx-auto">
        <CardHeader>
          <CardTitle className="text-2xl text-green-700">Surgrolator - Create Blend</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div>
              <Label htmlFor="name">Blend Name</Label>
              <Controller
                name="name"
                control={control}
                render={({ field }) => <Input {...field} className="mt-1" />}
              />
              {errors.name && <p className="text-red-600 text-sm">{errors.name.message}</p>}
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label htmlFor="targetN">Nitrogen (%)</Label>
                <Controller
                  name="targetN"
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
                {errors.targetN && <p className="text-red-600 text-sm">{errors.targetN.message}</p>}
              </div>
              <div>
                <Label htmlFor="targetP">Phosphorus (P₂O₅ %)</Label>
                <Controller
                  name="targetP"
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
                {errors.targetP && <p className="text-red-600 text-sm">{errors.targetP.message}</p>}
              </div>
              <div>
                <Label htmlFor="targetK">Potassium (K₂O %)</Label>
                <Controller
                  name="targetK"
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
                {errors.targetK && <p className="text-red-600 text-sm">{errors.targetK.message}</p>}
              </div>
              <div>
                <Label htmlFor="targetS">Sulfur (%)</Label>
                <Controller
                  name="targetS"
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
                {errors.targetS && <p className="text-red-600 text-sm">{errors.targetS.message}</p>}
              </div>
              <div>
                <Label htmlFor="targetCa">Calcium (%)</Label>
                <Controller
                  name="targetCa"
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
                {errors.targetCa && <p className="text-red-600 text-sm">{errors.targetCa.message}</p>}
              </div>
              <div>
                <Label htmlFor="targetMg">Magnesium (%)</Label>
                <Controller
                  name="targetMg"
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
                {errors.targetMg && <p className="text-red-600 text-sm">{errors.targetMg.message}</p>}
              </div>
              <div>
                <Label htmlFor="targetFe">Iron (%)</Label>
                <Controller
                  name="targetFe"
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
                {errors.targetFe && <p className="text-red-600 text-sm">{errors.targetFe.message}</p>}
              </div>
              <div>
                <Label htmlFor="targetZn">Zinc (%)</Label>
                <Controller
                  name="targetZn"
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
                {errors.targetZn && <p className="text-red-600 text-sm">{errors.targetZn.message}</p>}
              </div>
              <div>
                <Label htmlFor="targetMn">Manganese (%)</Label>
                <Controller
                  name="targetMn"
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
                {errors.targetMn && <p className="text-red-600 text-sm">{errors.targetMn.message}</p>}
              </div>
              <div>
                <Label htmlFor="targetB">Boron (%)</Label>
                <Controller
                  name="targetB"
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
                {errors.targetB && <p className="text-red-600 text-sm">{errors.targetB.message}</p>}
              </div>
              <div>
                <Label htmlFor="targetCl">Chlorine (%)</Label>
                <Controller
                  name="targetCl"
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
                {errors.targetCl && <p className="text-red-600 text-sm">{errors.targetCl.message}</p>}
              </div>
            </div>
            <div>
              <Label htmlFor="applicationRate">Application Rate (lbs/acre)</Label>
              <Controller
                name="applicationRate"
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
              {errors.applicationRate && <p className="text-red-600 text-sm">{errors.applicationRate.message}</p>}
            </div>
            <div>
              <Label>Select Ingredients</Label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-1">
                {ingredients.map(ing => (
                  <div key={ing.id} className="flex items-center space-x-2">
                    <Controller
                      name="selectedIngredients"
                      control={control}
                      render={({ field }) => (
                        <Checkbox
                          checked={field.value.includes(ing.id)}
                          onCheckedChange={checked => {
                            const newValue = checked
                              ? [...field.value, ing.id]
                              : field.value.filter(id => id !== ing.id);
                            field.onChange(newValue);
                          }}
                        />
                      )}
                    />
                    <Label>{ing.name}</Label>
                  </div>
                ))}
              </div>
              {errors.selectedIngredients && <p className="text-red-600 text-sm">{errors.selectedIngredients.message}</p>}
            </div>
            <div>
              <Label>Select Chemicals</Label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-1">
                {chemicals.map(chem => (
                  <div key={chem.id} className="flex items-center space-x-2">
                    <Controller
                      name="selectedChemicals"
                      control={control}
                      render={({ field }) => (
                        <Checkbox
                          checked={field.value.includes(chem.id)}
                          onCheckedChange={checked => {
                            const newValue = checked
                              ? [...field.value, chem.id]
                              : field.value.filter(id => id !== chem.id);
                            field.onChange(newValue);
                          }}
                        />
                      )}
                    />
                    <Label>{chem.name}</Label>
                  </div>
                ))}
              </div>
            </div>
            {selectedChemicals.length > 0 && (
              <div>
                <Label>Chemical AI Percentages</Label>
                <div className="space-y-2 mt-1">
                  {selectedChemicals.map(id => {
                    const chem = chemicals.find(c => c.id === id);
                    return (
                      <div key={id} className="flex items-center gap-2">
                        <Label className="w-32">{chem?.name}</Label>
                        <Controller
                          name="chemicalQuantities"
                          control={control}
                          render={({ field }) => (
                            <Input
                              type="number"
                              placeholder="AI %"
                              value={field.value.find(q => q.chemicalId === id)?.aiPercentage || 0}
                              onChange={e => {
                                const newQuantities = [...field.value];
                                const index = newQuantities.findIndex(q => q.chemicalId === id);
                                if (index >= 0) {
                                  newQuantities[index].aiPercentage = parseFloat(e.target.value);
                                }
                                field.onChange(newQuantities);
                              }}
                              className="w-32"
                            />
                          )}
                        />
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
            <Button type="submit" className="w-full bg-green-600 hover:bg-green-700 text-white">
              Optimize & Save Blend
            </Button>
          </form>
          {blendResult && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold text-green-700">Blend Result</h3>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Quantity (lbs/acre)</TableHead>
                    <TableHead>Cost ($/acre)</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {Object.entries(blendResult)
                    .filter(([key]) => key !== 'cost' && key !== 'feasible' && key !== 'result')
                    .map(([key, quantity]) => ({
                      name: key.replace(/^(ing_|chem_)/, ''),
                      quantity,
                      cost: key.startsWith('ing_')
                        ? quantity * (ingredients.find(ing => `ing_${ing.name}` === key)?.costPerTon || 0) / 2000
                        : quantity * (chemicals.find(chem => `chem_${chem.name}` === key)?.costPerUnit || 0),
                      displayOrder: key.startsWith('ing_')
                        ? ingredients.find(ing => `ing_${ing.name}` === key)?.displayOrder || 0
                        : chemicals.find(chem => `chem_${chem.name}` === key)?.displayOrder || 0,
                    }))
                    .sort((a, b) => a.displayOrder - b.displayOrder)
                    .map(item => (
                      <TableRow key={item.name}>
                        <TableCell>{item.name}</TableCell>
                        <TableCell>{item.quantity.toFixed(2)}</TableCell>
                        <TableCell>${item.cost.toFixed(2)}</TableCell>
                      </TableRow>
                    ))}
                  <TableRow>
                    <TableCell colSpan={2} className="font-semibold">Total Cost</TableCell>
                    <TableCell className="font-semibold">${blendResult.cost.toFixed(2)}</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default BlendBuilder;
