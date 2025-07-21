import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { useForm, Controller } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { toast } from '@/components/ui/use-toast';
import { jsPDF } from 'jspdf';
import { blendsApi, quotesApi } from '@/services/api';

const tagSchema = z.object({
  blendId: z.number().optional(),
  customerName: z.string().min(1, 'Customer name is required'),
  manualIngredients: z.array(
    z.object({
      name: z.string().min(1, 'Ingredient name is required'),
      quantity: z.number().min(0, 'Quantity must be non-negative'),
    })
  ).optional(),
});

type TagForm = z.infer<typeof tagSchema>;
type Blend = { id: number; name: string; ingredients: { name: string; quantity: number }[] };

function QuoteBuilder() {
  const navigate = useNavigate();
  const [blends, setBlends] = useState<Blend[]>([]);
  const [selectedBlend, setSelectedBlend] = useState<Blend | null>(null);
  const { control, handleSubmit, watch, setValue } = useForm<TagForm>({
    resolver: zodResolver(tagSchema),
    defaultValues: { customerName: '', blendId: undefined, manualIngredients: [] },
  });

  useEffect(() => {
    // Fetch blends from backend
    const fetchBlends = async () => {
      try {
        const response = await blendsApi.getAll();
        setBlends(response.data);
      } catch (error) {
        toast({ variant: 'destructive', title: 'Error', description: 'Failed to fetch blends' });
      }
    };
    fetchBlends();
  }, []);

  const generatePDF = (data: TagForm) => {
    const doc = new jsPDF();
    doc.setFontSize(16);
    doc.text('SurBlend Tag', 20, 20);
    doc.setFontSize(12);
    doc.text(`Customer: ${data.customerName}`, 20, 30);
    doc.text(`Blend: ${selectedBlend?.name || 'Manual Entry'}`, 20, 40);
    doc.text('Ingredients:', 20, 50);
    const ingredients = selectedBlend?.ingredients || data.manualIngredients || [];
    ingredients.forEach((ing, index) => {
      doc.text(`${ing.name}: ${ing.quantity.toFixed(2)} lbs/acre`, 30, 60 + index * 10);
    });
    doc.save(`surblend-tag-${data.customerName}.pdf`);
  };

  const onSubmit = async (data: TagForm) => {
    try {
      const quoteData = {
        customerName: data.customerName,
        blendId: data.blendId,
        ingredients: selectedBlend?.ingredients || data.manualIngredients || [],
      };
      await quotesApi.create(quoteData);
      generatePDF(data);
      toast({ title: 'Success', description: 'Tag generated and saved' });
      navigate('/quotes');
    } catch (error) {
      toast({ variant: 'destructive', title: 'Error', description: 'Failed to save tag' });
    }
  };

  const blendId = watch('blendId');
  useEffect(() => {
    if (blendId) {
      const blend = blends.find(b => b.id === blendId);
      setSelectedBlend(blend || null);
      setValue('manualIngredients', []);
    } else {
      setSelectedBlend(null);
    }
  }, [blendId, blends, setValue]);

  return (
    <div className="container mx-auto p-6">
      <Card className="max-w-4xl mx-auto">
        <CardHeader>
          <CardTitle className="text-2xl text-green-700">SurGro Tag Generator</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div>
              <Label htmlFor="customerName">Customer Name</Label>
              <Controller
                name="customerName"
                control={control}
                render={({ field }) => <Input {...field} className="mt-1" />}
              />
            </div>
            <div>
              <Label htmlFor="blendId">Select Blend (Optional)</Label>
              <Controller
                name="blendId"
                control={control}
                render={({ field }) => (
                  <Select onValueChange={value => field.onChange(parseInt(value))} value={field.value?.toString()}>
                    <SelectTrigger className="mt-1">
                      <SelectValue placeholder="Select a blend or enter manually" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="0">Manual Entry</SelectItem>
                      {blends.map(blend => (
                        <SelectItem key={blend.id} value={blend.id.toString()}>
                          {blend.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}
              />
            </div>
            {!blendId && (
              <div>
                <Label>Manual Ingredients</Label>
                <Controller
                  name="manualIngredients"
                  control={control}
                  render={({ field }) => (
                    <div className="space-y-2">
                      {field.value?.map((ing, index) => (
                        <div key={index} className="flex gap-2">
                          <Input
                            placeholder="Ingredient Name"
                            value={ing.name}
                            onChange={e => {
                              const newIngredients = [...field.value];
                              newIngredients[index].name = e.target.value;
                              field.onChange(newIngredients);
                            }}
                          />
                          <Input
                            type="number"
                            placeholder="Quantity (lbs/acre)"
                            value={ing.quantity}
                            onChange={e => {
                              const newIngredients = [...field.value];
                              newIngredients[index].quantity = parseFloat(e.target.value);
                              field.onChange(newIngredients);
                            }}
                          />
                          <Button
                            type="button"
                            variant="destructive"
                            onClick={() => {
                              const newIngredients = field.value.filter((_, i) => i !== index);
                              field.onChange(newIngredients);
                            }}
                          >
                            Remove
                          </Button>
                        </div>
                      ))}
                      <Button
                        type="button"
                        className="mt-2"
                        onClick={() => field.onChange([...(field.value || []), { name: '', quantity: 0 }])}
                      >
                        Add Ingredient
                      </Button>
                    </div>
                  )}
                />
              </div>
            )}
            <Button type="submit" className="w-full bg-green-600 hover:bg-green-700 text-white">
              Generate Tag
            </Button>
          </form>
          {selectedBlend && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold text-green-700">Selected Blend</h3>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Ingredient</TableHead>
                    <TableHead>Quantity (lbs/acre)</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {selectedBlend.ingredients.map(ing => (
                    <TableRow key={ing.name}>
                      <TableCell>{ing.name}</TableCell>
                      <TableCell>{ing.quantity.toFixed(2)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default QuoteBuilder;
