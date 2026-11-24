#include <mgba/core/core.h>
#include <mgba-util/vfs.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <fcntl.h>

int main(int argc, char **argv) {
    if (argc != 3) { fprintf(stderr, "usage: smoke ROM output-prefix < input (frames mask)\n"); return 2; }
    struct mCore *core = mCoreCreate(mPLATFORM_GBA);
    if (!core || !core->init(core)) return 3;
    mCoreInitConfig(core, "smoke");
    struct VFile *rom = VFileOpen(argv[1], O_RDONLY);
    if (!rom || !core->loadROM(core, rom)) return 4;
    unsigned w,h; core->desiredVideoDimensions(core,&w,&h);
    color_t *pixels = calloc(w*h,sizeof(color_t)); if (!pixels) return 5;
    core->setVideoBuffer(core,pixels,w);
    core->reset(core);
    unsigned frames, mask, total=0, step=0;
    while (scanf("%u %u",&frames,&mask)==2) {
        if (frames>10000 || total+frames>200000 || mask>1023) return 6;
        core->setKeys(core,mask);
        for(unsigned i=0;i<frames;i++) core->runFrame(core);
        total+=frames;
        char name[1024]; snprintf(name,sizeof(name),"%s-%03u.ppm",argv[2],step++);
        FILE *f=fopen(name,"wb"); if(!f)return 7;
        fprintf(f,"P6\n%u %u\n255\n",w,h);
        for(unsigned i=0;i<w*h;i++){ uint32_t p=pixels[i]; unsigned char rgb[3]={p&255,(p>>8)&255,(p>>16)&255}; fwrite(rgb,1,3,f); }
        fclose(f); printf("frames=%u core=%u\n",total,core->frameCounter(core)); fflush(stdout);
    }
    core->deinit(core); free(pixels); return 0;
}
