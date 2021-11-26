// CodeMirror, copyright (c) by Marijn Haverbeke and others
// Distributed under an MIT license: http://codemirror.net/LICENSE

(function(mod) {
  if (typeof exports == "object" && typeof module == "object") // CommonJS
    mod(require("../../lib/codemirror"));
  else if (typeof define == "function" && define.amd) // AMD
    define(["../../lib/codemirror"], mod);
  else // Plain browser env
    mod(CodeMirror);
})(function(CodeMirror) {
"use strict";

CodeMirror.defineMode("octave", function() {
  function wordRegexp(words) {
    return new RegExp("^((" + words.join(")|(") + "))\\b");
  }

  var singleOperators = new RegExp("^[\\+\\-\\*/&|\\^~<>!@'\\\\]");
  var singleDelimiters = new RegExp('^[\\(\\[\\{\\},:=;]');
  var doubleOperators = new RegExp("^((==)|(~=)|(<=)|(>=)|(<<)|(>>)|(\\.[\\+\\-\\*/\\^\\\\]))");
  var doubleDelimiters = new RegExp("^((!=)|(\\+=)|(\\-=)|(\\*=)|(/=)|(&=)|(\\|=)|(\\^=))");
  var tripleDelimiters = new RegExp("^((>>=)|(<<=))");
  var expressionEnd = new RegExp("^[\\]\\)]");
  var identifiers = new RegExp("^[_A-Za-z\xa1-\uffff][_A-Za-z0-9\xa1-\uffff]*");

  var builtins = wordRegexp([
    'abs','accumarray','accumdim','acos','acosd','acosh','acot','acotd','acoth','acsc','acscd','acsch','addlistener','addpath','addpref','addproperty','addtodate','add_input_event_hook','airy','all','allchild','allow_noninteger_range_as_index','amd','ancestor','and','angle','annotation','anova','any','arch_fit','arch_rnd','arch_test','area','arg','argnames','argv','arma_rnd','arrayfun','ascii','asctime','asec','asecd','asech','asin','asind','asinh','assert','assignin','atan','atan2','atan2d','atand','atanh','atexit','audiodevinfo','audioformats','audioinfo','audioplayer','audioread','audiorecorder','audiowrite','autoload','autoreg_matrix','autumn','available_graphics_toolkits','axes','axis','balance','bandwidth','bar','barh','bartlett','bartlett_test','base2dec','base64_decode','base64_encode','beep','beep_on_error','besselh','besseli','besselj','besselk','bessely','beta','betacdf',
    'betainc','betaincinv','betainv','betaln','betapdf','betarnd','bicg','bicgstab','bin2dec','binary','bincoeff','binocdf','binoinv','binopdf','binornd','bitand','bitcmp','bitget','bitor','bitpack','bitset','bitshift','bitunpack','bitxor','blackman','blanks','blkdiag','blkmm','bone','box','brighten','bsxfun','builtin','built_in_docstrings_file','bunzip2','byte_size','bzip2','calendar','camlight','canonicalize_file_name','cart2pol','cart2sph','cast','cat','cauchy_cdf','cauchy_inv','cauchy_pdf','cauchy_rnd','caxis','cbrt','ccolamd','cd','ceil','cell','cell2mat','cell2struct','celldisp','cellfun','cellindexmat','cellslices','cellstr','center','cgs','char','chdir','chi2cdf','chi2inv','chi2pdf','chi2rnd','chisquare_test_homogeneity','chisquare_test_independence','chol','chol2inv','choldelete','cholinsert','cholinv','cholshift','cholupdate','chop','circshift','citation','cla','clabel',
    'class','clc','clear','clf','clock','cloglog','close','closereq','cmpermute','cmunique','colamd','colloc','colon','colorbar','colorcube','colormap','colperm','colstyle','columns','comet','comet3','command_line_path','common_size','commutation_matrix','compan','compare_versions','compass','completion_append_char','completion_matches','complex','computer','cond','condeig','condest','confirm_recursive_rmdir','conj','contour','contour3','contourc','contourf','contrast','conv','conv2','convhull','convhulln','convn','cool','copper','copyfile','copyobj','corr','cor_test','cos','cosd','cosh','cot','cotd','coth','cov','cplxpair','cputime','crash_dumps_octave_core','cross','csc','cscd','csch','cstrcat','csvread','csvwrite','csymamd','ctime','ctranspose','cubehelix','cummax','cummin','cumprod','cumsum','cumtrapz','curl','cylinder','daspect','daspk','daspk_options','dasrt','dasrt_options',
    'dassl','dassl_options','date','datenum','datestr','datetick','datevec','dawson','dbclear','dbcont','dbdown','dblist','dblquad','dbnext','dbquit','dbstack','dbstatus','dbstep','dbstop','dbtype','dbup','dbwhere','deal','deblank','debug_java','debug_jit','debug_on_error','debug_on_interrupt','debug_on_warning','dec2base','dec2bin','dec2hex','deconv','deg2rad','del2','delaunay','delaunayn','delete','dellistener','demo','desktop','det','detrend','diag','dialog','diary','diff','diffpara','diffuse','dims','dir','dir_in_loadpath','disable_diagonal_matrix','disable_permutation_matrix','disable_range',
    'discrete_cdf','discrete_inv','discrete_pdf','discrete_rnd','disp','display','divergence','dlmread','dlmwrite','dmperm','doc','doc_cache_create','doc_cache_file','dos','dot','double','do_braindead_shortcircuit_evaluation','do_string_escapes','drawnow','dsearch','dsearchn','dup2','duplication_matrix','durbinlevinson','e','echo','echo_executing_commands','edit','EDITOR','edit_history','eig','eigs','elem','ellipj','ellipke','ellipsoid','empirical_cdf','empirical_inv','empirical_pdf','empirical_rnd','endgrent','endpwent','eomday','eps','eq','erf','erfc','erfcinv','erfcx','erfi','erfinv','errno','errno_list','error','errorbar','errordlg','etime','etree','etreeplot','eval','evalc','evalin','example','exec','EXEC_PATH','exist','exit','exp','expcdf','expint','expinv','expm','expm1','exppdf','exprnd','eye','ezcontour','ezcontourf','ezmesh','ezmeshc','ezplot','ezplot3','ezpolar','ezsurf',
    'ezsurfc','factor','factorial','fail','false','fcdf','fclear','fclose','fcntl','fdisp','feather','feof','ferror','feval','fflush','fft','fft2','fftconv','fftfilt','fftn','fftshift','fftw','fgetl','fgets','fieldnames','figure','fileattrib','filemarker','fileparts','fileread','filesep','file_in_loadpath','file_in_path','fill','filter','filter2','find','findall','findfigs','findobj','findstr','finv','fix','fixed_point_format','flag','flintmax','flip','fliplr','flipud','floor','fminbnd','fminsearch','fminunc','foo','fopen','fork','format','formula','fortran_vec','fpdf','fplot','fprintf','fputs','fractdiff','frame2im','fread','freport','freqz','freqz_plot','frewind','frnd','fscanf','fseek','fskipl','fsolve','ftell','ftp','full','fullfile','func2str','functions','fwrite','fzero','f_test_regression','gallery','gamcdf','gaminv','gamma','gammainc','gammaln','gampdf','gamrnd','gca','gcbf',
    'gcbo','gcd','gcf','gco','ge','genpath','genvarname','geocdf','geoinv','geopdf','geornd','get','getappdata','getaudiodata','getegid','getenv','geteuid','getfield','getgid','getgrent','getgrgid','getgrnam','gethostname','getpgrp','getpid','getplayer','getppid','getpref','getpwent','getpwnam','getpwuid','getrusage','getuid','get_first_help_sentence','get_help_text','get_help_text_from_file','get_home_directory','ginput','givens','glob','glpk','gls','gmres','gmtime','gnuplot_binary','gplot','grabcode','gradient','graphics_toolkit','gray','gray2ind','grid','griddata','griddata3','griddatan','gt','gtext','guidata','guihandles','gunzip','gzip','hadamard','hamming','hankel','hanning','hash','have_window_system','hdl2struct','help','helpdlg','hess','hex2dec','hex2num','hggroup','hgload','hgsave','hidden','hilb','hist','histc','history','history_control','history_file','history_save',
    'history_size','history_timestamp_format_string','hold','home','horzcat','hot','hotelling_test','hotelling_test_2','housh','hsv','hsv2rgb','hurst','hygecdf','hygeinv','hygepdf','hygernd','hypot','i','I','ichol','idivide','ifelse','ifft','ifft2','ifftn','ifftshift','ignore_function_time_stamp','ilu','im2double','im2frame','imag','image','imagesc','IMAGE_PATH','imfinfo','imformats','importdata','imread','imshow','imwrite','ind2gray','ind2rgb','ind2sub','index','inf','Inf','inferiorto','info','info_file','info_program','inline','inpolygon','input','inputdlg','inputname','inputParser',
    'inputParser.CaseSensitive','inputParser.FunctionName','inputParser.KeepUnmatched','inputParser.Parameters','inputParser.Results','inputParser.StructExpand','inputParser.Unmatched','inputParser.UsingDefaults','int16','int2str','int32','int64','int8','interp1','interp2','interp3','interpft','interpn','intersect','intmax','intmin','inv','invhilb','ipermute','iqr','isa','isalnum','isalpha','isappdata','isargout','isascii','isaxes','isbanded','isbool','iscell','iscellstr','ischar','iscntrl','iscolormap','iscolumn','iscomplex','isdebugmode','isdefinite','isdeployed','isdiag','isdigit','isdir','isempty','isequal','isequaln','isfield','isfigure','isfinite','isfloat','isglobal','isgraph','isguirunning','ishandle','ishermitian','ishghandle','ishold','isieee','isindex','isinf','isinteger','isjava','iskeyword','isletter','islogical','islower','ismac','ismatrix','ismember','ismethod',
    'isna','isnan','isnull','isnumeric','isobject','isocaps','isocolors','isonormals','isosurface','ispc','isplaying','ispref','isprime','isprint','isprop','ispunct','isreal','isrecording','isrow','isscalar','issorted','isspace','issparse','issquare','isstrprop','isstruct','isstudent','issymmetric','istril','istriu','isunix','isupper','isvarname','isvector','isxdigit','is_absolute_filename','is_dq_string','is_function_handle','is_leap_year','is_rooted_relative_filename','is_sq_string','is_valid_file_id','j','J','javaaddpath','javaArray','javachk','javaclasspath','javamem','javaMethod','javaObject','javarmpath','java_get','java_matrix_autoconversion','java_set','java_unsigned_autoconversion','jet','jit_enable','jit_failcnt','jit_startcnt','kbhit','kendall','keyboard','kill','kolmogorov_smirnov_cdf','kolmogorov_smirnov_test','kolmogorov_smirnov_test_2','kron','kruskal_wallis_test',
    'krylov','kurtosis','laplace_cdf','laplace_inv','laplace_pdf','laplace_rnd','lasterr','lasterror','lastwarn','lcm','ldivide','le','legend','legendre','length','lgamma','license','light','lighting','lin2mu','line','lines','link','linkaxes','linkprop','linsolve','linspace','listdlg','list_in_columns','list_primes','load','loaded_graphics_toolkits','loadobj','localfunctions','localtime','log','log10','log1p','log2','logical','logistic_cdf','logistic_inv','logistic_pdf','logistic_regression','logistic_rnd','logit','loglog','loglogerr','logm','logncdf','logninv','lognpdf','lognrnd','logspace','lookfor','lookup','lower','ls','lscov','lsode','lsode_options','lsqnonneg','lstat','ls_command','lt','lu','luupdate','magic','makeinfo_program','make_absolute_filename','manova','mat2cell','mat2str','material','matlabroot','matrix_type','max','max_recursion_depth','mcnemar_test','mean',
    'meansq','median','menu','merge','mesh','meshc','meshgrid','meshz','methods','mex','mexext','mfilename','mget','mgorth','min','minus','mislocked','missing_component_hook','missing_function_hook','mkdir','mkfifo','mkoctfile','mkpp','mkstemp','mktime','mldivide','mlock','mod','mode','moment','more','movefile','mpoles','mpower','mput','mrdivide','msgbox','mtimes','mu2lin','munlock','NA','namelengthmax','nan','NaN','nargin','narginchk','nargout','nargoutchk','native_float_format','nbincdf','nbininv','nbinpdf','nbinrnd','nchoosek','ndgrid','ndims','ne','newplot','news','nextpow2','nnz','nonzeros','norm','normcdf','normest','normest1','norminv','normpdf','normrnd','not','now','nproc','nthargout','nthroot','nth_element','ntsc2rgb','null','num2cell','num2hex','num2str','numel','numfields','nzmax','ocean','octave_core_file_limit','octave_core_file_name','octave_core_file_options',
    'ode23','ode45','odeget','odeplot','odeset','ols','onCleanup','ones','open','operator','optimget','optimize_subsasgn_calls','optimset','or','orderfields','ordschur','orient','orth','ostrsplit','output_max_field_width','output_precision','pack','padecoef','PAGER','PAGER_FLAGS','page_output_immediately','page_screen_output','pan','pareto','parseparams','pascal','patch','path','pathdef','pathsep','pause','pbaspect','pcg','pchip','pclose','pcolor','pcr','peaks','periodogram','perl','perms','permute','pi','pie','pie3','pink','pinv','pipe','pkg','planerot','play','playblocking',
    'plot','plot3','plotmatrix','plotyy','plus','poisscdf','poissinv','poisspdf','poissrnd','pol2cart','polar','poly','polyaffine','polyarea','polyder','polyeig','polyfit','polygcd','polyint','polyout','polyreduce','polyval','polyvalm','popen','popen2','postpad','pow2','power','powerset','ppder','ppint','ppjumps','ppplot','ppval','pqpnonneg','prctile','prefdir','preferences','prepad','primes','print','printd','printf','print_empty_dimensions','print_struct_array_contents','print_usage','prism','probit','prod','profexplore','profexport','profile','profshow','program_invocation_name','program_name','prop_test_2','PS1','PS2','PS4','psi','publish','putenv','puts','pwd','python','P_tmpdir','qmr','qp','qqplot','qr','qrdelete','qrinsert','qrshift','qrupdate','quad','quadcc','quadgk','quadl','quadv','quad_options','quantile','questdlg','quit','quiver','quiver3','qz','qzhess',
    'rad2deg','rainbow','rand','rande','randg','randi','randn','randp','randperm','range','rank','ranks','rat','rats','rcond','rdivide','readdir','readline_read_init_file','readline_re_read_init_file','readlink','real','reallog','realmax','realmin','realpow','realsqrt','record','recordblocking','rectangle','rectint','recycle','reducepatch','reducevolume','refresh','refreshdata','regexp','regexpi','regexprep','regexptranslate','register_graphics_toolkit','rehash','rem','remove_input_event_hook','rename','repelems','repmat','reset','reshape','residue','resize','restoredefaultpath','resume','rethrow','return','rgb2hsv','rgb2ind','rgb2ntsc','rgbplot','ribbon','rindex','rmappdata','rmdir','rmfield','rmpath','rmpref','roots','rose','rosser','rot90','rotate','rotate3d','rotdim','round','roundb','rows','rref','rsf2csf','run','rundemos','runlength','runtests','run_count','run_history',
    'run_test','save','saveas','saveobj','savepath','save_default_options','save_header_format_string','save_precision','scanf','scatter','scatter3','schur','sec','secd','sech','SEEK_CUR','SEEK_END','SEEK_SET','semilogx','semilogxerr','semilogy','semilogyerr','set','setappdata','setdiff','setenv','setfield','setgrent','setpref','setpwent','setxor','shading','shg','shift','shiftdim','shrinkfaces','SIG','sighup_dumps_octave_core','sign','signbit','sign_test','sigterm_dumps_octave_core','silent_functions','sin','sinc','sind','sinetone','sinewave','single','sinh','size','sizemax','sizeof','size_equal','skewness','slice','smooth3','sombrero','sort','sortrows','sound','soundsc','source','spalloc','sparse','sparse_auto_mutate','spaugment','spconvert','spdiags','spearman','spectral_adf','spectral_xdf','specular','speed','spencer','speye','spfun','sph2cart','sphere','spinmap','spline',
    'splinefit','split_long_rows','spones','spparms','sprand','sprandn','sprandsym','sprank','spring','sprintf','spstats','spy','sqp','sqrt','sqrtm','squeeze','sscanf','stairs','stat','statistics','std','stderr','stdin','stdnormal_cdf','stdnormal_inv','stdnormal_pdf','stdnormal_rnd','stdout','stem','stem3','stemleaf','stft','stop','str2double','str2func','str2num','strcat','strchr','strcmp','strcmpi','strfind','strftime','string_fill_char','strjoin','strjust','strmatch','strncmp','strncmpi','strptime','strread','strrep','strsplit','strtok','strtrim','strtrunc','struct','struct2cell','struct2hdl','structfun','struct_levels_to_print','strvcat','sub2ind','subplot','subsasgn','subsindex','subspace','subsref','substr','substruct','sum','summer','sumsq','superiorto','suppress_verbose_help_message','surf','surface','surfc','surfl','surfnorm','svd','svds','svd_driver','swapbytes',
    'sylvester','symamd','symbfact','symlink','symrcm','symvar','synthesis','system','S_ISBLK','S_ISCHR','S_ISDIR','S_ISFIFO','S_ISLNK','S_ISREG','S_ISSOCK','table','tan','tand','tanh','tar','tcdf','tempdir','tempname','terminal_size','test','tetramesh','texi_macros_file','text','textread','textscan','tic','tilde_expand','time','times','tinv','title','tmpfile','toascii','toc','toeplitz','tolower','toupper','tpdf','trace','transpose','trapz','treelayout','treeplot','tril','trimesh','triplequad','triplot','trisurf','triu','trnd','true','tsearch','tsearchn','type','typecast','typeinfo','t_test','t_test_2','t_test_regression',
    'uibuttongroup','uicontextmenu','uicontrol','uigetdir','uigetfile','uimenu','uint16','uint32','uint64','uint8','uipanel','uipushtool','uiputfile','uiresume','uitoggletool','uitoolbar','uiwait','umask','uminus','uname','undo_string_escapes','unidcdf','unidinv','unidpdf','unidrnd','unifcdf','unifinv','unifpdf','unifrnd','union','unique','unix','unlink','unmkpp','unpack','unsetenv','untabify','untar','unwrap','unzip','uplus','upper','urlread','urlwrite','usejava','u_test','validateattributes','validatestring','vander','var','var_test','vec','vech','vectorize','ver','version','vertcat','view','viridis','voronoi','voronoin','waitbar','waitfor','waitforbuttonpress','waitpid','warndlg','warning','warranty','waterfall','wblcdf','wblinv','wblpdf','wblrnd','WCONTINUE','WCOREDUMP','weekday','welch_test','WEXITSTATUS','what','which','white','whitebg','who','whos','whos_line_format',
    'wienrnd','WIFCONTINUED','WIFEXITED','WIFSIGNALED','WIFSTOPPED','wilcoxon_test','wilkinson','winter','WNOHANG','WSTOPSIG','WTERMSIG','WUNTRACED','xlabel','xlim','xor','yes_or_no','ylim','yulewalker','zeros','zip','zlim','zoom','zscore','z_test'
  ]);

  var keywords = wordRegexp([
    'return', 'case', 'switch', 'else', 'elseif', 'end', 'endif', 'endfunction',
    'if', 'otherwise', 'do', 'for', 'while', 'try', 'catch', 'classdef', 'properties', 'events',
    'methods', 'global', 'persistent', 'endfor', 'endwhile', 'printf', 'sprintf', 'disp', 'until',
    'continue', 'pkg'
  ]);


  // tokenizers
  function tokenTranspose(stream, state) {
    if (!stream.sol() && stream.peek() === '\'') {
      stream.next();
      state.tokenize = tokenBase;
      return 'operator';
    }
    state.tokenize = tokenBase;
    return tokenBase(stream, state);
  }


  function tokenComment(stream, state) {
    if (stream.match(/^.*%}/)) {
      state.tokenize = tokenBase;
      return 'comment';
    };
    stream.skipToEnd();
    return 'comment';
  }

  function tokenBase(stream, state) {
    // whitespaces
    if (stream.eatSpace()) return null;

    // Handle one line Comments
    if (stream.match('%{')){
      state.tokenize = tokenComment;
      stream.skipToEnd();
      return 'comment';
    }

    if (stream.match(/^[%#]/)){
      stream.skipToEnd();
      return 'comment';
    }

    // Handle Number Literals
    if (stream.match(/^[0-9\.+-]/, false)) {
      if (stream.match(/^[+-]?0x[0-9a-fA-F]+[ij]?/)) {
        stream.tokenize = tokenBase;
        return 'number'; };
      if (stream.match(/^[+-]?\d*\.\d+([EeDd][+-]?\d+)?[ij]?/)) { return 'number'; };
      if (stream.match(/^[+-]?\d+([EeDd][+-]?\d+)?[ij]?/)) { return 'number'; };
    }
    if (stream.match(wordRegexp(['nan','NaN','inf','Inf']))) { return 'number'; };

    // Handle Strings
    var m = stream.match(/^"(?:[^"]|"")*("|$)/) || stream.match(/^'(?:[^']|'')*('|$)/)
    if (m) { return m[1] ? 'string' : "string error"; }

    // Handle words
    if (stream.match(keywords)) { return 'keyword'; } ;
    if (stream.match(builtins)) { return 'builtin'; } ;
    if (stream.match(identifiers)) { return 'variable'; } ;

    if (stream.match(singleOperators) || stream.match(doubleOperators)) { return 'operator'; };
    if (stream.match(singleDelimiters) || stream.match(doubleDelimiters) || stream.match(tripleDelimiters)) { return null; };

    if (stream.match(expressionEnd)) {
      state.tokenize = tokenTranspose;
      return null;
    };


    // Handle non-detected items
    stream.next();
    return 'error';
  };


  return {
    startState: function() {
      return {
        tokenize: tokenBase
      };
    },

    token: function(stream, state) {
      var style = state.tokenize(stream, state);
      if (style === 'number' || style === 'variable'){
        state.tokenize = tokenTranspose;
      }
      return style;
    },

    lineComment: '%',

    fold: 'indent'
  };
});

CodeMirror.defineMIME("text/x-octave", "octave");

});
