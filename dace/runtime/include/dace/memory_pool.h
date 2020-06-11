#ifndef __DACE_MEMORYPOOL_H
#define __DACE_MEMORYPOOL_H

//template <bool IS_GPU>

class MemoryPool
{
private:
    size_t m_size, m_offset;
    size_t m_reserved;
    void* m_mem;

    void Init()
    {
        size_t total, free;

        size_t alloc_size;
        if (m_reserved == 0){
            printf("ERROR: Please reserve Memory before allocating!");
            exit(1);
        }

        alloc_size = m_reserved;
        //if (IS_GPU)
        //    m_mem = cudaMalloc(alloc_size);
        //else
        //printf("%f", (double)alloc_size);
        m_mem = calloc(alloc_size, sizeof(double));
        if (m_mem == NULL){
            printf("ERROR: Allocation failed");
            exit(1);
        }
        m_size = alloc_size;
        m_offset = 0;
    }

public:
    MemoryPool(): m_mem(nullptr), m_size(0), m_offset(0), m_reserved(0){}

    void ReserveMemory(size_t membytes)
    {
        if (m_size > 0)
            {
                printf("ERROR: Cannot reserve memory - memory already allocated\n");
                return;
            }
        m_reserved = membytes;
    }

    void* Alloc(size_t size, size_t block_size)
    {
        if (m_size == 0) Init();

        if (size > m_size - m_offset)
        {
            printf("\n\n Warning: bad context allocation, exiting. \n\n");
            exit(1);
        }

        size_t offset = m_offset;
        int int_size = (size / block_size + 1) * block_size * sizeof(double);
        m_offset += int_size;
        //printf("here");
        //printf("%d \n", (int)size);
        //printf("%d \n",(int)offset);
        //printf("%d \n", (int)m_offset);
        //printf("%d \n", (int)int_size);
        return (void*)((char*)m_mem + offset);
    }

};

#endif // __DACE_MEMORYPOOL_H