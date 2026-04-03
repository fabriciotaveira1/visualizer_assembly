import { Navigate, Route, Routes } from "react-router-dom";

import Layout from "../components/Layout";
import Dashboard from "../pages/Dashboard";
import Login from "../pages/Login";
import CriarAssembleia from "../pages/assembleias/CriarAssembleia";
import DetalheAssembleia from "../pages/assembleias/DetalheAssembleia";
import ListarAssembleias from "../pages/assembleias/ListarAssembleias";
import CriarCondominio from "../pages/condominios/CriarCondominio";
import ListarCondominios from "../pages/condominios/ListarCondominios";
import CriarUnidade from "../pages/unidades/CriarUnidade";
import ListarUnidades from "../pages/unidades/ListarUnidades";
import Votacao from "../pages/votacao/Votacao";
import useAuth from "../hooks/useAuth";

function PrivateRoute({ children }) {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

export default function AppRoutes() {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      <Route
        path="/login"
        element={
          isAuthenticated ? <Navigate to="/dashboard" replace /> : <Login />
        }
      />
      <Route
        path="/dashboard"
        element={
          <PrivateRoute>
            <Layout>
              <Dashboard />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/condominios"
        element={
          <PrivateRoute>
            <Layout>
              <ListarCondominios />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/condominios/novo"
        element={
          <PrivateRoute>
            <Layout>
              <CriarCondominio />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/unidades"
        element={
          <PrivateRoute>
            <Layout>
              <ListarUnidades />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/unidades/novo"
        element={
          <PrivateRoute>
            <Layout>
              <CriarUnidade />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/assembleias"
        element={
          <PrivateRoute>
            <Layout>
              <ListarAssembleias />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/assembleias/nova"
        element={
          <PrivateRoute>
            <Layout>
              <CriarAssembleia />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/assembleias/:id"
        element={
          <PrivateRoute>
            <Layout>
              <DetalheAssembleia />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/assembleias/:id/votacao"
        element={
          <PrivateRoute>
            <Layout>
              <Votacao />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="*"
        element={
          <Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />
        }
      />
    </Routes>
  );
}
