#include <cstdio>
#include <cuda_runtime.h>
#include <cstdlib>

#define CK(x) do{cudaError_t e=(x); if(e){printf("ERR %s @%d\n",cudaGetErrorString(e),__LINE__);return 1;}}while(0)

__global__ void readk(const float4* __restrict__ a, size_t n, float* out){
    float4 s = make_float4(0,0,0,0);
    for(size_t i = blockIdx.x*(size_t)blockDim.x + threadIdx.x; i < n; i += (size_t)gridDim.x*blockDim.x){
        float4 v = a[i]; s.x+=v.x; s.y+=v.y; s.z+=v.z; s.w+=v.w;
    }
    if(s.x==1234.5f) out[0]=s.x+s.y+s.z+s.w;   // never taken, keeps loads live
}
__global__ void copyk(const float4* __restrict__ a, float4* __restrict__ b, size_t n){
    for(size_t i = blockIdx.x*(size_t)blockDim.x + threadIdx.x; i < n; i += (size_t)gridDim.x*blockDim.x)
        b[i] = a[i];
}

int main(int argc, char** argv){
    int dev = argc>1 ? atoi(argv[1]) : 0;
    CK(cudaSetDevice(dev));
    cudaDeviceProp p; CK(cudaGetDeviceProperties(&p,dev));
    double peak = 2.0*p.memoryClockRate*1e3*(p.memoryBusWidth/8)/1e9;
    printf("GPU%d %s  sm_%d%d  memclk %.0f MHz  bus %d bit  theoretical %.0f GB/s\n",
           dev,p.name,p.major,p.minor,p.memoryClockRate/1e3,p.memoryBusWidth,peak);

    size_t bytes = (size_t)(argc>2?atoi(argv[2]):256)<<20;
    size_t n = bytes/sizeof(float4);
    float4 *a,*b; float* out;
    CK(cudaMalloc(&a,bytes)); CK(cudaMalloc(&b,bytes)); CK(cudaMalloc(&out,sizeof(float)*4));
    CK(cudaMemset(a,1,bytes));
    int blocks = p.multiProcessorCount*32, threads=256;
    cudaEvent_t e0,e1; cudaEventCreate(&e0); cudaEventCreate(&e1);
    float ms;

    for(int w=0;w<2;w++){ readk<<<blocks,threads>>>(a,n,out); } CK(cudaDeviceSynchronize());
    cudaEventRecord(e0);
    for(int r=0;r<10;r++) readk<<<blocks,threads>>>(a,n,out);
    cudaEventRecord(e1); CK(cudaDeviceSynchronize()); cudaEventElapsedTime(&ms,e0,e1);
    printf("  read-only      %7.1f GB/s  (%.1f%% of theoretical)\n", 10.0*bytes/(ms*1e6), 100.0*(10.0*bytes/(ms*1e6))/peak);

    copyk<<<blocks,threads>>>(a,b,n); CK(cudaDeviceSynchronize());
    cudaEventRecord(e0);
    for(int r=0;r<10;r++) copyk<<<blocks,threads>>>(a,b,n);
    cudaEventRecord(e1); CK(cudaDeviceSynchronize()); cudaEventElapsedTime(&ms,e0,e1);
    printf("  copy (r+w)     %7.1f GB/s  (%.1f%% of theoretical)\n", 20.0*bytes/(ms*1e6), 100.0*(20.0*bytes/(ms*1e6))/peak);

    cudaEventRecord(e0);
    for(int r=0;r<10;r++) CK(cudaMemcpy(b,a,bytes,cudaMemcpyDeviceToDevice));
    cudaEventRecord(e1); CK(cudaDeviceSynchronize()); cudaEventElapsedTime(&ms,e0,e1);
    printf("  memcpyD2D(r+w) %7.1f GB/s  (%.1f%% of theoretical)\n", 20.0*bytes/(ms*1e6), 100.0*(20.0*bytes/(ms*1e6))/peak);
    return 0;
}
