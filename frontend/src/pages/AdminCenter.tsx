import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Users, Settings } from 'lucide-react';

function AdminCenter() {
  const navigate = useNavigate();

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold text-green-900 mb-6">Admin Center</h1>
      <div className="flex flex-col gap-4 max-w-md mx-auto">
        <Card className="rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 bg-white">
          <CardHeader>
            <CardTitle className="flex items-center text-lg text-green-700">
              <Users className="mr-2 h-5 w-5" />
              User Management
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">Manage user roles and permissions.</p>
            <Button
              onClick={() => navigate('/users')}
              className="w-full bg-green-600 hover:bg-green-700 text-white rounded-lg"
            >
              Manage Users
            </Button>
          </CardContent>
        </Card>
        <Card className="rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 bg-white">
          <CardHeader>
            <CardTitle className="flex items-center text-lg text-green-700">
              <Settings className="mr-2 h-5 w-5" />
              System Settings
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">Configure system settings and tools.</p>
            <Button
              onClick={() => navigate('/settings')}
              className="w-full bg-green-600 hover:bg-green-700 text-white rounded-lg"
            >
              Configure Settings
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default AdminCenter;
