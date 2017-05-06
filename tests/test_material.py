#!/usr/bin/env/python
"""
Pyrate - Optical raytracing based on Python

Copyright (C) 2017 Moritz Esslinger <moritz.esslinger@web.de>
               and Johannes Hartung <j.hartung@gmx.net>
               and     Uwe Lippmann <uwe.lippmann@web.de>
               and    Thomas Heinze <t.heinze@fn.de>

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""
import numpy as np
import sympy
from core.localcoordinates import LocalCoordinates
from core.material import AnisotropicMaterial

def test_anisotropic_xi_calculation_polynomial():
    '''
    Random epsilon tensor, Random k vector and n unit vector in z direction.
    Polynomial coefficients for eigenvalue equation from
    the numerical calculations via np.einsum and the analytical expressions
    given below (p4a, ..., p0a) should be identical. The test should work 
    for real and complex epsilon and k values.
    '''
    lc = LocalCoordinates("1")
    
    myeps = np.random.random((3, 3)) + complex(0, 1)*np.random.random((3, 3))
    ((epsxx, epsxy, epsxz), (epsyx, epsyy, epsyz), (epszx, epszy, epszz)) = \
        tuple(myeps)
    
    m = AnisotropicMaterial(lc, myeps)
    
    n = np.zeros((3, 5))
    n[2, :] = 1.    
    
    x = np.zeros((3, 5))
    k = np.random.random((3, 5)) + complex(0, 1)*np.random.random((3, 5))
    
    kpa = k - np.sum(n * k, axis=0)*n

    kx = kpa[0]
    ky = kpa[1]

    (p4v, p3v, p2v, p1v, p0v) = m.calcXiPolynomial(x, n, kpa)

    # TODO: Maybe generalize to arbitrary n vectors

    p4a = epszz*np.ones_like(kx)
    p3a = (epsxz + epszx)*kx + (epsyz + epszy)*ky
    p2a = epsxz*epszx + epsyz*epszy - (epsxx + epsyy)*epszz \
        + (epsxx + epszz)*kx**2 + (epsxy + epsyx)*kx*ky \
        + (epsyy + epszz)*ky**2
    p1a = (epsxz + epszx)*kx**3 \
        + (epsxz*epsyx + epsxy*epszx - epsxx*(epsyz + epszy))*ky \
        + (epsyz + epszy)*kx**2*ky + (epsyz + epszy)*ky**3 \
        + kx*(-(epsxz*epsyy) + epsxy*epsyz - epsyy*epszx + epsyx*epszy + (epsxz + epszx)*ky**2)
    p0a = -(epsxz*epsyy*epszx) + epsxy*epsyz*epszx + epsxz*epsyx*epszy \
        - epsxx*epsyz*epszy - epsxy*epsyx*epszz + epsxx*epsyy*epszz \
        + epsxx*kx**4 + (epsxy + epsyx)*kx**3*ky \
        + (epsxy*epsyx - epsxx*epsyy + epsyz*epszy - epsyy*epszz)*ky**2 \
        + epsyy*ky**4 + kx**2*(epsxy*epsyx + epsxz*epszx - epsxx*(epsyy + epszz) \
            + (epsxx + epsyy)*ky**2) + kx*(\
                (epsyz*epszx + epsxz*epszy - (epsxy + epsyx)*epszz)*ky \
                + (epsxy + epsyx)*ky**3
            )
    
    should_be_zero_4 = p4a - p4v    
    assert np.allclose(should_be_zero_4, 0)
    should_be_zero_3 = p3a - p3v    
    assert np.allclose(should_be_zero_3, 0)
    should_be_zero_2 = p2a - p2v    
    assert np.allclose(should_be_zero_2, 0)    
    should_be_zero_1 = p1a - p1v    
    assert np.allclose(should_be_zero_1, 0)    
    should_be_zero_0 = p0a - p0v    
    assert np.allclose(should_be_zero_0, 0)    
    
def test_anisotropic_xi_calculation_det():
    '''
    Random epsilon tensor, Random k vector and n unit vector in z direction.
    Determinant of the propagator from numerical calculations 
    via np.einsum and from analytical expression given below should coincide.
    The test should work for real and complex epsilon and k values.
    '''
    lc = LocalCoordinates("1")
    
    myeps = np.random.random((3, 3)) + complex(0, 1)*np.random.random((3, 3))
    ((epsxx, epsxy, epsxz), (epsyx, epsyy, epsyz), (epszx, epszy, epszz)) = \
        tuple(myeps)
    
    m = AnisotropicMaterial(lc, myeps)
    
    n = np.zeros((3, 5))
    n[2, :] = 1.    
    
    x = np.zeros((3, 5))
    k = np.random.random((3, 5)) + complex(0, 1)*np.random.random((3, 5))
    xi = np.random.random((5,)) + complex(0, 1)*np.random.random((5,))    
    
    
    kpa = k - np.sum(n * k, axis=0)*n

    kx = kpa[0]
    ky = kpa[1]

    # TODO: Maybe generalize to arbitrary n vectors

    

    det_analytical = xi**4*epszz \
                    + xi**3*((epsxz + epszx)*kx + (epsyz + epszy)*ky)\
                    + xi**2*(epsxz*epszx + epsyz*epszy - (epsxx + epsyy)*epszz\
                        + (epsxx + epszz)*kx**2 + (epsxy + epsyx)*kx*ky\
                        + (epsyy + epszz)*ky**2)\
                    + xi*((epsxz + epszx)*kx**3\
                        + (epsxz*epsyx + epsxy*epszx - epsxx*(epsyz + epszy))*ky\
                        + (epsyz + epszy)*kx**2*ky + (epsyz + epszy)*ky**3\
                        + kx*(-(epsxz*epsyy) + epsxy*epsyz - epsyy*epszx\
                            + epsyx*epszy + (epsxz + epszx)*ky**2))\
                    -(epsxz*epsyy*epszx) + epsxy*epsyz*epszx\
                    + epsxz*epsyx*epszy - epsxx*epsyz*epszy\
                    - epsxy*epsyx*epszz + epsxx*epsyy*epszz + epsxx*kx**4\
                    + (epsxy + epsyx)*kx**3*ky \
                    + (epsxy*epsyx - epsxx*epsyy + epsyz*epszy - epsyy*epszz)*ky**2 \
                    + epsyy*ky**4 + kx**2*(epsxy*epsyx + epsxz*epszx \
                        - epsxx*(epsyy + epszz) + (epsxx + epsyy)*ky**2)\
                    + kx*((epsyz*epszx + epsxz*epszy \
                        - (epsxy + epsyx)*epszz)*ky + (epsxy + epsyx)*ky**3)
                        
    should_be_zero = det_analytical - m.calcXiDet(xi, x, n, kpa)
    assert np.allclose(should_be_zero, 0)


def test_anisotropic_xi_calculation_polynomial_zeros():
    '''
    Random epsilon tensor, random k vector and random n unit vector.
    Check whether the roots calculated give really zero for the determinant.
    The test should work for real and complex epsilon and k values.
    '''
    lc = LocalCoordinates("1")
    
    myeps = np.random.random((3, 3)) + complex(0, 1)*np.random.random((3, 3))
    ((epsxx, epsxy, epsxz), (epsyx, epsyy, epsyz), (epszx, epszy, epszz)) = \
        tuple(myeps)
    
    m = AnisotropicMaterial(lc, myeps)
    
    n = np.random.random((3, 5))
    n = n/np.sqrt(np.sum(n*n, axis=0))
    
    x = np.zeros((3, 5))
    k = np.random.random((3, 5)) + complex(0, 1)*np.random.random((3, 5))
    
    kpa = k - np.sum(n * k, axis=0)*n


    should_be_zero = np.ones((4, 5), dtype=complex)
    xiarray = m.calcXiNormZeros(x, n, kpa)
    for i in range(4):
        should_be_zero[i, :] = m.calcXiDet(xiarray[i], x, n, kpa)
    
    assert np.allclose(should_be_zero, 0)

def test_anisotropic_xi_eigenvalues():
    """
    Comparison of eigenvalue calculation for xi from random complex material
    data. Comparing polynomial calculation from determinant, from quadratic
    eigenvalue problem and analytical calculation from sympy.
    """
    lc = LocalCoordinates("1")
    
    myeps = np.zeros((3, 3), dtype=complex)
    myeps[0:2, 0:2] = np.random.random((2, 2)) + complex(0, 1)*np.random.random((2, 2))
    myeps[2, 2] = np.random.random() + complex(0, 1)*np.random.random()
    #np.random.random((3, 3)) + complex(0, 1)*np.random.random((3, 3))
    ((epsxx, epsxy, epsxz), (epsyx, epsyy, epsyz), (epszx, epszy, epszz)) = \
        tuple(myeps)
    
    m = AnisotropicMaterial(lc, myeps)
    
    #n = np.random.random((3, 1))
    #n = n/np.sqrt(np.sum(n*n, axis=0))
    n = np.zeros((3, 1))
    n[2, :] = 1    
    
    x = np.zeros((3, 1))
    k = np.random.random((3, 1)) + complex(0, 1)*np.random.random((3, 1))
    
    kpa = k - np.sum(n * k, axis=0)*n
    
    (eigenvalues, eigenvectors) = m.calcXiEigenvectors(x, n, kpa)

    xiarray = m.calcXiNormZeros(x, n, kpa)
    
    
#            for k in range(6):
#                evr = vr[:, k].reshape(6, 1)
#                print(np.dot(Mmatrix[:, :, j]*w[k]**2 + Cmatrix[:, :, j]*w[k] + Kmatrix[:, :, j], evr[3:]))
#                print(np.linalg.det(Mmatrix[:, :, j]*w[k]**2 + Cmatrix[:, :, j]*w[k] + Kmatrix[:, :, j]))            
#                print(np.linalg.det(Amatrix6x6[:, :, j] - Bmatrix6x6[:, :, j]*w[k]))            
#                            
#            
#            print(np.array_str(w))
#            #print(np.array_str(Amatrix6x6[:, :, j], precision=2, suppress_small=True))
#            #print(np.array_str(Bmatrix6x6[:, :, j], precision=2, suppress_small=True))
#            print(self.calcXiDet(w[3], x, n, kpa_norm))            
#            print(np.linalg.det(Mmatrix[:, :, j]*xiarray[0, j]**2 + Cmatrix[:, :, j]*xiarray[0, j] + Kmatrix[:, :, j]))            
#        
#        print(xiarray)

    
    # sympy check with analytical solution
    kx, ky, xi = sympy.symbols('k_x k_y xi')
    exx, exy, exz, eyx, eyy, eyz, ezx, ezy, ezz \
        = sympy.symbols('e_xx e_xy e_xz e_yx e_yy e_yz e_zx e_zy e_zz')
        
    #eps = Matrix([[exx, exy, exz], [eyx, eyy, eyz], [ezx, ezy, ezz]])
    eps = sympy.Matrix([[exx, exy, 0], [eyx, eyy, 0], [0, 0, ezz]])
    v = sympy.Matrix([[kx, ky, xi]])
    m = -(v*v.T)[0]*sympy.eye(3) + v.T*v + eps
    detm = m.det().collect(xi)
        
    soldetm = sympy.solve(detm, xi)
    subsdict = {
        kx:kpa[0, 0],
        ky:kpa[1, 0],
        exx:epsxx,
        exy:epsxy,
        eyx:epsyx,
        eyy:epsyy,
        ezz:epszz,
        sympy.I:complex(0, 1)
        }
    analytical_solution = np.sort(np.array([sol.evalf(subs=subsdict) for sol in soldetm], dtype=complex))
    numerical_solution1 = np.sort(xiarray[:, 0])
    numerical_solution2 = np.sort(eigenvalues[:, 0])
    
    assert np.allclose(analytical_solution - numerical_solution1, 0)
    assert np.allclose(analytical_solution - numerical_solution2, 0)

# TODO: consistency checks
# c) (quadratic eigenvalue problem) ev = 0


def test_anisotropic_xi_determinants():
    """
    Check whether xi zeros from polynomial fulfill the QEVP and the 
    associated GLEVP. This also verifies whether A6x6 and B6x6 are
    constructed correctly.
    """
    lc = LocalCoordinates("1")
    
    myeps = np.random.random((3, 3)) + complex(0, 1)*np.random.random((3, 3))
    ((epsxx, epsxy, epsxz), (epsyx, epsyy, epsyz), (epszx, epszy, epszz)) = \
        tuple(myeps)
    
    m = AnisotropicMaterial(lc, myeps)
    
    n = np.random.random((3, 5))
    n = n/np.sqrt(np.sum(n*n, axis=0))
    
    x = np.zeros((3, 5))
    k = np.random.random((3, 5)) + complex(0, 1)*np.random.random((3, 5))
    
    kpa = k - np.sum(n * k, axis=0)*n

    xiarray = m.calcXiNormZeros(x, n, kpa)

    ((Amatrix6x6, Bmatrix6x6), (Mmatrix, Cmatrix, Kmatrix)) = m.calcXiQEVMatrices(x, n, kpa)

    should_be_zero_1 = np.ones((4, 5), dtype=complex)
    should_be_zero_2 = np.ones((4, 5), dtype=complex)
    for j in range(5):
        for xi_num in range(4):
            should_be_zero_1[xi_num, j] = np.linalg.det(Mmatrix[:, :, j]*xiarray[xi_num, j]**2 + Cmatrix[:, :, j]*xiarray[xi_num, j] + Kmatrix[:, :, j])
            should_be_zero_2[xi_num, j] = np.linalg.det(Amatrix6x6[:, :, j] - Bmatrix6x6[:, :, j]*xiarray[xi_num, j])

    assert np.allclose(should_be_zero_1, 0)
    assert np.allclose(should_be_zero_2, 0)    
    
if __name__=="__main__":
    test_anisotropic_xi_determinants()
