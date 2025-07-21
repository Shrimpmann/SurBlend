import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Sprout, Tag, Users, Package, BarChart2, Settings, FlaskConical } from 'lucide-react';
import BlendBuilder from '@/pages/blends/BlendBuilder';
import TagGenerator from '@/pages/tags/TagGenerator';
import Chemicals from '@/pages/chemicals/Chemicals';

<Route path="/blends/new" element={<BlendBuilder />} />
<Route path="/tags/new" element={<TagGenerator />} />
<Route path="/chemicals" element={<Chemicals />} />

function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold text-green-900 mb-6">
        Welcome, {user?.full_name || user?.username || 'User'}!
      </h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-w-5xl mx-auto">
        <Card className="rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 bg-white">
          <CardHeader>
            <CardTitle className="flex items-center text-lg text-green-700">
              <Sprout className="mr-2 h-5 w-5" />
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
            <p className="text-gray-600 mb-4">Generate tags for blends or manual entries.</p>
            <Button
              onClick={() => navigate('/tags/new')}
              className="w-full bg-green-600 hover:bg-green-700 text-white rounded-lg"
            >
              Create Tag
            </Button>
          </CardContent>
        </Card>
        <Card className="rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 bg-white">
          <CardHeader>
            <CardTitle className="flex items-center text-lg text-green-700">
              <Package className="mr-2 h-5 w-5" />
              Ingredient Management
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">Manage fertilizer ingredients and nutrient profiles.</p>
            <Button
              onClick={() => navigate('/ingredients')}
              className="w-full bg-green-600 hover:bg-green-700 text-white rounded-lg"
            >
              Manage Ingredients
            </Button>
          </CardContent>
        </Card>
        <Card className="rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 bg-white">
          <CardHeader>
            <CardTitle className="flex items-center text-lg text-green-700">
              <Users className="mr-2 h-5 w-5" />
              Customer Profiles
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">Manage customers, farms, and preferred blends.</p>
            <Button
              onClick={() => navigate('/customers')}
              className="w-full bg-green-600 hover:bg-green-700 text-white rounded-lg"
            >
              View Customers
            </Button>
          </CardContent>
        </Card>
        <Card className="rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 bg-white">
          <CardHeader>
            <CardTitle className="flex items-center text-lg text-green-700">
              <BarChart2 className="mr-2 h-5 w-5" />
              Analytics
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">Analyze blend and tag trends.</p>
            <Button
              onClick={() => navigate('/analytics')}
              className="w-full bg-green-600 hover:bg-green-700 text-white rounded-lg"
            >
              View Analytics
            </Button>
          </CardContent>
        </Card>
        {user?.role === 'ADMIN' && (
          <Card className="rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 bg-white">
            <CardHeader>
              <CardTitle className="flex items-center text-lg text-green-700">
                <FlaskConical className="mr-2 h-5 w-5" />
                Chemicals Management
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 mb-4">Manage chemicals and their properties.</p>
              <Button
                onClick={() => navigate('/chemicals')}
                className="w-full bg-green-600 hover:bg-green-700 text-white rounded-lg"
              >
                Manage Chemicals
              </Button>
            </CardContent>
          </Card>
        )}
        {user?.role === 'ADMIN' && (
          <Card className="rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 bg-white">
            <CardHeader>
              <CardTitle className="flex items-center text-lg text-green-700">
                <Settings className="mr-2 h-5 w-5" />
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
