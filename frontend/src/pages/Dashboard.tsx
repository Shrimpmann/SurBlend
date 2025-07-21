import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Blend, Tag } from 'lucide-react';

function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold text-green-900 mb-6">
        Welcome, {user?.full_name || user?.username}!
      </h1>
      <div className="flex flex-col gap-4 max-w-md mx-auto">
        <Card className="rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 bg-white">
          <CardHeader>
            <CardTitle className="flex items-center text-lg text-green-700">
              <Blend className="mr-2 h-5 w-5" />
              Surgrolator
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">Create and optimize fertilizer blends with least-cost formulation.</p>
            <Button
              onClick={() => navigate('/blends/new')}
              className="w-full bg-green-600 hover:bg-green-700 text-white rounded-lg"
            >
              Start Blending
            </Button>
          </CardContent>
        </Card>
        <Card className="rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 bg-white">
          <CardHeader>
            <CardTitle className="flex items-center text-lg text-green-700">
              <Tag className="mr-2 h-5 w-5" />
              SurGro Tag Generator
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">Generate quotes and blend tags for customers.</p>
            <Button
              onClick={() => navigate('/quotes/new')}
              className="w-full bg-green-600 hover:bg-green-700 text-white rounded-lg"
            >
              Create Quote
            </Button>
          </CardContent>
        </Card>
        {user?.role === 'ADMIN' && (
          <Card className="rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 bg-white">
            <CardHeader>
              <CardTitle className="flex items-center text-lg text-green-700">
                Admin Center
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 mb-4">Manage users, settings, and system tools.</p>
              <Button
                onClick={() => navigate('/admin')}
                className="w-full bg-green-600 hover:bg-green-700 text-white rounded-lg"
              >
                Go to Admin Center
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
